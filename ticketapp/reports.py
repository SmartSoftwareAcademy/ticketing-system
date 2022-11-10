from reportlab.platypus.paragraph import Paragraph
from reportlab.lib import pagesizes
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import xlwt
from django.http import HttpResponse
from datetime import datetime
from .models import *
from django.shortcuts import render
import re
from django.utils.html import strip_tags
from reportlab.platypus import *
from django.utils.formats import date_format
import os
from reportlab.pdfgen import canvas
from pathlib import Path
from reportlab.platypus import PageBreak, SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib.units import inch, cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from django.contrib.auth.models import User
from django.db.models import Q
import pdb
import urllib

def ReportView(request):
    staff = User.objects.all().values_list('email')
    clients = Ticket.objects.all().values_list("customer_email")
    return render(request, "ticketapp/reporting.html", {"staffs": staff, "clients": clients})


def ABSOLUTE_PATH():
    return Path(__file__).resolve().parent.parent


def export_tickets_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    file_name=f'tickets_{datetime.now().day}_{datetime.now().hour}_{datetime.now().minute}_{datetime.now().second}.xls'
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    wb = xlwt.Workbook(encoding='utf-8')
    # this will make a sheet named Users Data
    ws = wb.add_sheet('Tickets Data')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Ticket Issue','Raised BY', 'Date Raised',
               'Date Ressolved', 'Ressolved By', 'Issue Description', ]

    for col_num in range(len(columns)):
        # at 0 row 0 column
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    if request.POST != None or '':
        print(request.POST)
        resolved = ""
        unsolved = ""
        urgent = ""
        pending = ""
        datefrom = request.POST['datefrom']
        dateto = request.POST['dateto']
        cemail = request.POST.getlist('client_mails')[0]
        semail = request.POST.getlist('staff_mails')[0]
        rows = []
        if 'pending' in request.POST:
            pending = request.POST['pending']
            tckts=Ticket.objects.filter(Q(ticket_status__contains=pending)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if 'unsolved' in request.POST:
            unsolved = request.POST['unsolved']
            tckts=Ticket.objects.filter(Q(ticket_status__contains=unsolved)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if 'urgent' in request.POST:
            urgent = request.POST['urgent']
            tckts=Ticket.objects.filter(Q(ticket_status__contains=urgent)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if 'ressolved' in request.POST:
            resolved = request.POST['ressolved']
            tckts=Ticket.objects.filter(Q(ticket_status__contains=resolved)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if datefrom != '' and dateto != '':
            datefrom = request.POST['datefrom']
            dateto = request.POST['dateto']
            tckts=Ticket.objects.filter(created_date__range=[datefrom,dateto]).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if semail != 'select staff' or  cemail != 'select client':
            semail = semail[2:-3]
            cemail = cemail[2:-3]
            tckts=Ticket.objects.filter(Q(resolved_by__email__contains=semail) | Q(customer_email__contains=cemail)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
    else:
        rows = Ticket.objects.all().values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
        pdb.set_trace()
    #print(rows)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            inrow = str(row[col_num])
            if len(inrow) > 32767 or len(inrow):
                inrow = inrow[0:32766]
                # replace &nbsp; with space and strip html tags
                inrow = re.sub(r'(?<!&nbsp;)&nbsp;', ' ', strip_tags(inrow))
            else:
                inrow = re.sub(r'(?<!&nbsp;)&nbsp;', ' ', strip_tags(inrow))
            ws.write(row_num, col_num, inrow, font_style)
    wb.save(response)

    return response


# Custom Canvas class for automatically adding page-numbers
class MyCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def draw_page_number(self, page_count):
        # Modify the content and styles according to the requirement
        page = "Copyright © {} Gokhanmasterspace JV Limited. All Rights Reserved. Page {curr_page} of {total_pages}".format(datetime.now(
        ).year, curr_page=self._pageNumber, total_pages=page_count)
        self.setFont("Helvetica", 12)
        self.drawRightString(250*mm, 8*mm, page)

    def save(self):
        # Modify the save() function to add page-number before saving every page
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)


def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    file_name=f'tickets_{datetime.now().day}_{datetime.now().hour}_{datetime.now().minute}_{datetime.now().second}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    styles = getSampleStyleSheet()

    PAGESIZE = pagesizes.landscape(pagesizes.A3)

    doc = SimpleDocTemplate(response, pagesize=PAGESIZE,
                            leftMargin=1 * cm,
                            rightMargin=1 * cm,
                            topMargin=1 * cm,
                            bottomMargin=1 * cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Normal_CENTER',
                              parent=styles['Normal'],
                              fontName='Helvetica',
                              wordWrap='LTR',
                              alignment=TA_CENTER,
                              fontSize=14,
                              leading=14,
                              textColor=colors.black,
                              borderPadding=2,
                              leftIndent=0,
                              rightIndent=0,
                              spaceAfter=1,
                              spaceBefore=1,
                              splitLongWords=True,
                              spaceShrinkage=0.05,
                              ))
    styles.add(ParagraphStyle(name='Normal_LEFT',
                              parent=styles['Normal'],
                              fontName='Helvetica',
                              wordWrap='LTR',
                              alignment=TA_LEFT,
                              fontSize=16,
                              leading=16,
                              textColor=colors.black,
                              borderPadding=2,
                              leftIndent=0,
                              rightIndent=0,
                              spaceAfter=1,
                              spaceBefore=1,
                              splitLongWords=True,
                              spaceShrinkage=0.05,
                              ))
    header_l0 = Paragraph(
        "Gokhanmasterspace JV Limited", styles['Normal_CENTER'])
    header_l1 = Paragraph(
        "First Floor,Birdi Complex,", styles['Normal_CENTER'])
    header_l2 = Paragraph("Mombasa Road-Nairobi,Kenya",
                          styles['Normal_CENTER'])
    header_l3 = Paragraph("Phone:+254-715-837-832", styles['Normal_CENTER'])
    header_l4 = Paragraph("Email: info@masterspace.co.ke",
                          styles['Normal_CENTER'])
    header_l5 = Paragraph("P.O Box: 36779-00200", styles['Normal_CENTER'])
    header_l6 = Paragraph("Ticket Reports as at {}".format(
        datetime.now()), styles['Normal_LEFT'])

    setup=System_Settings.objects.first()
    if setup != None:
        logo= str(ABSOLUTE_PATH())+str(setup.logo.url)
    else:
        logo = os.path.join(ABSOLUTE_PATH(), "static", "img", "logo.png")
    im = Image(logo, 2 * inch, 2 * inch)

    rows = []
    data = []
    data.append(im)
    data.append(header_l0)
    data.append(header_l1)
    data.append(header_l2)
    data.append(header_l4)
    data.append(header_l3)
    data.append(header_l5)
    data.append(header_l6)
    tickets = Ticket.objects.all()  # filter(ticket_status="Resolved")
    headers = ["Ticket Issue", "Raised By",
               "Ressolved By", "Date Raised", "Date Ressolved", "Duration\n(Days:Hours)"]
    rows.append(headers)
    for ticket in tickets:
        duration = ""
        title = Paragraph(ticket.title, styles['BodyText'])
        cemail = Paragraph(ticket.customer_email, styles['BodyText'])
        semail = [Paragraph(ticket.resolved_by.email, styles['BodyText']) if ticket.resolved_by !=
                  None else "Not Ressolved"][0]
        if ticket.resolved_date != None:
            duration = "D:"+str((ticket.resolved_date-ticket.created_date).days) + \
                " H:"+str("{:.2f}".format((ticket.resolved_date -
                          ticket.created_date).seconds/(3600)))
        else:
            duration = "Unknown"
        rows.append([title,
                     cemail,
                     semail,
                     date_format(ticket.created_date, "SHORT_DATE_FORMAT"),
                     [date_format(ticket.resolved_date, "SHORT_DATE_FORMAT")
                      if ticket.resolved_date != None else "Not Ressolved"][0],
                     duration,
                     ])
    c_width = [5*inch, 3*inch, 3*inch, 1.5 *
               inch, 1.5*inch]
    content_table = Table(rows, rowHeights=40, colWidths=c_width)
    content_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, 'black'), ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                           ('FONTSIZE', (0, 0), (-1, -1), 12), ('ROWBACKGROUNDS', (0, 1), (-1, -2), ['lightgrey', 'white']), ]))
    data.append(content_table)
    data.append(PageBreak())
    doc.build(data, canvasmaker=MyCanvas)
    return response
