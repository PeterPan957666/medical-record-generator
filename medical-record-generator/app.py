from flask import Flask, request, jsonify, render_template, session, url_for
from flask_cors import CORS
from openai import OpenAI
import os
import json

# 创建 Flask 应用实例
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
app.secret_key = "62348975698"

# DeepSeek 配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-374841ab56aa400bad1265ea745ab992')
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# AI 病历生成规则
RULES = """
身份：你是一名临床病历生成 AI。
目标:根据医生口述生成两份病历:一份供医师使用的【标准化病历】(按模板、字段全覆盖、零推测、ICD 编码等），一份供患者阅读的【患者易懂版说明书】（通俗、量化、含复诊和风险提示）。
请严格遵守以下规范：
一、国家法规与政策
--1.中华人民共和国国家卫生健康委员会(2022年6月1日)发布的《关于印发医疗机构门诊质量管理暂行规定的通知》（文号：国卫办医发（2022）8号）
--2.中华人民共和国国家卫生健康委员会（2017年2月22日）发布的《电子病历应用管理规范（试行）》（文号：国卫办医发(2017)8号）
--3.中华人民共和国原卫生部（2010年1月22日）发布的《病历书写基本规范》（文号：卫医政发（2010）11号）
--4.国家卫生健康委员会、国家中医药局、国家疾控局（2025年6月）联合发布的《关于进一步加强医疗电子病历信息使用管理的通知》

二、行业指南与共识​
--1.国家卫生健康委员会（2015年7月24日）发布的《抗菌药物临床应用指导原则（2015年版）》（文号：国卫办医发（2015）43号）
--2.国家卫生健康委员会（2018年4月18日）发布的《医疗质量安全核心制度要点》（文号：国卫医发（2018）8号）

三、技术伦理与安全规范​
--1.全国人民代表大会常务委员会（2016年11月7日）发布的《中华人民共和国网络安全法》（主席令第五十三号）
--2.全国人民代表大会常务委员会（2021年8月20日）发布的《中华人民共和国个人信息保护法（主席令第九十一号）
--3.国家互联网信息办公室等七部门（2023年7月10日）联合发布《生成式人工智能服务管理暂行办法》

四、 医院内部规范​​
--1.​川北医学院附属医院医务科制定​​《川北医学院附属医院住院病历书写实施细则》​​
--2.​川北医学院附属医院药学部制定​​《川北医学院附属医院药品处方集》​

请严格遵守以下模板与原则：
- 零推测：信息仅取自医生口述，缺失用【未提供】标注。
- 生命体征必全：T/P/R/BP 全列，注明"实测/未测（原因）/未记录"。
- 诊断精确：含分型/分期 + ICD-11 编码 + 诊断依据（检查日期+结果）。
- 检查溯源：辅助检查必须含日期、全称、关键数值、结论。
- 治疗分层：分"立即执行 / 紧急检查 / 后续管理"，并注明指南来源。
- 缺失归因：未做项目必须说明原因。
- 风险透明：患者说明列风险、禁忌、替代方案。
- 患者双语：患者版需"通俗解释 + 量化标准"。
- 时间精确：发病/就诊时间精确到分钟，格式 `YYYY-MM-DD HH:MM`。
- 法律合规：遵守病历书写规范，可写"初步/待排"。
- AI声明：末尾必须有"本记录基于医生口述生成，需医师审核签名确认"。
- 字段全覆盖：所有字段必须出现，即使为空。
输出要求：最终只返回一个 **严格的 JSON**（不要混杂其它说明），JSON 必须包含两个字符串字段：
{
  "doctor_record": "<医生版病历（Markdown或结构化文本）>",
  "patient_record": "<患者易懂版说明书（可为多段文本）>"
}
不要输出任何额外的文字或注释，确保 JSON 格式可被程序解析。

医生标准版病历：
【主诉】：
【时间轴】：  
- 发病时间：  
- 就诊时间：  
【现病史】：  
【既往史】： 
【过敏史】： 
【体格检查】：  
- 一般情况：  
- 生命体征：  
  - 体温：  
  - 脉搏：  
  - 呼吸：  
  - 血压：  
- 专科检查： 
【辅助检查】：  
- [检查项目]：[状态/结果]  
【初步诊断】：  
【治疗建议】：  
1. 立即执行：  
2. 紧急检查：  
3. 后续管理：  
【AI声明】: 本记录基于医生口述生成，需医师审核签名确认。  
---

患者易懂版说明书：
① 病情说明：  
② 治疗方案： 
③ 时间轴管理： 
④ 风险与警示：
⑤ 生活干预： 
⑥ 复诊节点：  
【AI声明】: 本说明基于医生口述生成，需医师审核签名确认。  
"""

def generate_record(doctor_input: str):
    """生成病历记录"""
    prompt_messages = [
        {"role": "system", "content": RULES},
        {"role": "user", "content": f"医生口述：{doctor_input}\n\n请严格按规则输出 JSON。"}
    ]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=prompt_messages
        )
        text = response.choices[0].message.content.strip()
        try:
            data = json.loads(text)
            doctor = data.get("doctor_record", "")
            patient = data.get("patient_record", "")
        except Exception:
            doctor = text
            patient = "【未生成或模型输出非 JSON】"
        return {"doctor": doctor, "patient": patient}
    except Exception as e:
        print(f"病历生成失败: {str(e)}")
        return {"doctor": "病历生成服务暂时不可用", "patient": "请稍后再试"}

# Flask 路由
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    doctor_input = data.get("doctor_input", "").strip()
    if not doctor_input:
        return jsonify({"error": "医生口述不能为空"}), 400
    
    result = generate_record(doctor_input)
    session["doctor_record"] = result["doctor"]
    session["patient_record"] = result["patient"]
    return jsonify({"redirect": url_for("record_page")})

@app.route("/record")
def record_page():
    doctor = session.get("doctor_record", "没有病历，请返回首页生成。")
    patient = session.get("patient_record", "没有病历，请返回首页生成。")
    return render_template("record.html", doctor_record=doctor, patient_record=patient)

@app.route("/test_images")
def test_images():
    """测试所有图片是否可访问"""
    images = [
        "deepseek_LOGO.png",
        "背景.png",
        "病历智解官LOGO.png",
        "川北医LOGO.png",
        "医院LOGO.png",
        "麦克风_LOGO.png"
    ]
    
    html = "<h1>图片测试页</h1>"
    for img in images:
        url = url_for('static', filename=f'img/{img}')
        html += f'<h2>{img}</h2>'
        html += f''
        html += f'<p>访问地址: <a href="{url}">{url}</a></p><hr>'
    
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)