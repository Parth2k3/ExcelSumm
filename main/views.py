from django.shortcuts import render, redirect
import pandas as pd
from django.conf import settings
from django.http import HttpResponse
import os
from django.core.mail import EmailMessage

def handle_uploaded_file(file):
    df = pd.read_excel(file)
    summary = df.groupby(['Cust State', 'Cust Pin']).size().reset_index(name='DPD')
    base_dir = settings.BASE_DIR
    file_path = os.path.join(base_dir, 'customer_summary.xlsx')
    summary.to_excel(file_path, index=False)

    return summary, file_path

def send_summary_via_email(summary, file_path, recipient_email):
    summary_text = summary.to_string(index=False)
    email = EmailMessage(
        'Python Assessment - Parth Nangroo', 
        f'Please find the summary report below:\n\n{summary_text}',
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
    )

    email.attach_file(file_path)

    email.send()

def main(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    if request.method == 'POST':
        print(request.FILES)
        file = request.FILES.get('file')
        summary, file_path = handle_uploaded_file(file)
        recipient_email = 'tech@themedius.ai'
        send_summary_via_email(summary, file_path, recipient_email)
        request.session['summary_html'] = summary.to_html(index=False)
        request.session['file_path'] = file_path
        return redirect('result')


def result(request):
    summary_html = request.session.get('summary_html', '')
    file_path = request.session.get('file_path', '')

    return render(request, 'result.html', {
        'summary_html': summary_html,
        'file_path': file_path,
    })

def download_file(request):
    file_path = request.GET.get('file_path')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    return HttpResponse('File not found')