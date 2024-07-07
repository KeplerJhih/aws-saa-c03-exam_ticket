import os
import re
import random
from io import StringIO, BytesIO
from datetime import date
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfWriter, PdfReader

# 注册中文字体（请确保你有这个字体文件，或替换为你系统中的其他中文字体）
pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))

def extract_questions_from_pdf(pdf_path):
    questions = []
    output_string = StringIO()
    with open(pdf_path, 'rb') as file:
        extract_text_to_fp(file, output_string, laparams=LAParams(), output_type='text', codec='utf-8')
    text = output_string.getvalue()

    text = re.sub(r'店长微信：\w+', '', text)
    question_blocks = re.split(r'(?=问题\s*#?\d+|问题编号\s*\d+)', text)

    for block in question_blocks[1:]:
        lines = block.split('\n')
        question_number = ""
        question_text = []
        options = []
        answer = None
        in_options = False

        for line in lines:
            line = line.strip()
            if re.match(r'(问题\s*#?\d+|问题编号\s*\d+)', line):
                question_number = line
            elif re.match(r'^[A-F]\.', line):
                in_options = True
                options.append(line)
            elif '正确答案' in line:
                answer_match = re.search(r'正确答案[:：]\s*([A-F]+)', line)
                if answer_match:
                    answer = answer_match.group(1)
                else:
                    print(f"警告：在问题 {question_number} 中没有找到正确答案格式")
                in_options = False
            elif in_options and line:
                if options:
                    options[-1] += ' ' + line
                else:
                    question_text.append(line)
            elif line and not line.startswith('您的答案是'):
                question_text.append(line)

        if question_number and question_text:
            question_text = ' '.join(question_text)
            question_text = re.sub(r'\s+', ' ', question_text)
            question_text = re.sub(r'AWS\s+AWS。.*$', '', question_text)
            questions.append({
                "number": question_number,
                "question": question_text,
                "options": options,
                "answer": answer
            })

    print(f"從 {pdf_path} 中提取了 {len(questions)} 個問題")
    return questions

def add_incorrect_answer_to_pdf(incorrect_answer, filename):
    temp_buffer = BytesIO()
    doc = SimpleDocTemplate(temp_buffer, pagesize=letter, 
                            rightMargin=72, leftMargin=72, 
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Chinese', 
                              fontName='SimSun', 
                              fontSize=10, 
                              leading=14))

    story = []

    question_text = re.sub(r'\s+', ' ', incorrect_answer['question'])
    question_text = re.sub(r'AWS\s+AWS。.*$', '', question_text)

    story.append(Paragraph(incorrect_answer['number'], styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph(question_text, styles['Chinese']))
    story.append(Spacer(1, 0.1*inch))

    for option in incorrect_answer['options']:
        story.append(Paragraph(option, styles['Chinese']))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph(f"正确答案：{incorrect_answer['correct_answer']}", styles['Chinese']))
    story.append(Paragraph(f"您的答案：{incorrect_answer['user_answer']}", styles['Chinese']))
    story.append(Spacer(1, 0.2*inch))

    doc.build(story)

    temp_buffer.seek(0)
    new_pdf = PdfReader(temp_buffer)
    
    if os.path.exists(filename):
        existing_pdf = PdfReader(open(filename, "rb"))
        output = PdfWriter()
        for page in existing_pdf.pages:
            output.add_page(page)
    else:
        output = PdfWriter()

    output.add_page(new_pdf.pages[0])

    with open(filename, "wb") as outputStream:
        output.write(outputStream)

    print(f"错误答案已添加到 {filename}")

def quiz(questions, num_questions):
    random.shuffle(questions)  # 随机打乱题目顺序
    selected_questions = questions[:num_questions]  # 选择指定数量的题目
    total_questions = len(selected_questions)
    correct_count = 0

    os.makedirs('err', exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    filename = os.path.join('err', f"{today}.pdf")

    for index, q in enumerate(selected_questions, 1):
        print(f"\n{q['number']}")
        print(q['question'])
        for option in q['options']:
            print(option)
        
        user_answer = input("\n您的答案是 (可多选，用逗号分隔，如 A,B): ").upper().replace(" ", "")
        user_answer_set = set(user_answer.split(','))
        
        if q['answer'] is None:
            print("警告：此问题没有正确答案。")
            correct_answer_set = set()
        else:
            correct_answer_set = set(q['answer'])
        
        if user_answer_set == correct_answer_set:
            print("正确!")
            correct_count += 1
        else:
            print(f"不正确。正确答案是 {','.join(sorted(correct_answer_set)) if correct_answer_set else '未知'}。")
            incorrect_answer = {
                "number": q['number'],
                "question": q['question'],
                "options": q['options'],
                "correct_answer": q['answer'] if q['answer'] is not None else "未知",
                "user_answer": user_answer
            }
            add_incorrect_answer_to_pdf(incorrect_answer, filename)
        
        print(f"\n--- 问题 {index}/{total_questions} 完成 ---")
        print("-" * 40)

    print(f"\n测验完成！您的得分是 {correct_count}/{total_questions}。")

if __name__ == "__main__":
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("当前目录下没有找到PDF文件。")
    else:
        all_questions = []
        for pdf_file in pdf_files:
            print(f"正在处理文件：{pdf_file}")
            questions = extract_questions_from_pdf(pdf_file)
            all_questions.extend(questions)
            print(f"当前总问题数：{len(all_questions)}")
        
        print(f"\n总共找到 {len(all_questions)} 个问题。")
        
        num_questions = int(input("请输入您想练习的题目数量："))
        while num_questions <= 0 or num_questions > len(all_questions):
            print(f"请输入一个在1到{len(all_questions)}之间的数字。")
            num_questions = int(input("请重新输入您想练习的题目数量："))
        
        print("\n测验开始！")
        print("=" * 40)
        quiz(all_questions, num_questions)
        print("=" * 40)
        print("测验结束！")