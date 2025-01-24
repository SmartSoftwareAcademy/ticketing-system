from reportlab.platypus.paragraph import Paragraph
from reportlab.lib import pagesizes
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import xlwt
from django.http import HttpResponse
from datetime import datetime,timedelta
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
    if request.POST:
        resolved = ""
        unsolved = ""
        urgent = ""
        pending = ""
        datefrom = request.POST.get('datefrom','')
        dateto =  request.POST.get('datefrom','')
        cemail = request.POST.getlist('client_mails',['select client'])[0]
        semail = request.POST.getlist('staff_mails',['select staff'])[0]
        if pending !="":
            pending = request.POST['pending']
            tckts=Ticket.objects.filter(Q(ticket_status__contains=pending)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if unsolved !="":
            unsolved = request.POST['unsolved']
            tckts=Ticket.objects.filter(Q(ticket_status__contains=unsolved)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if urgent !="":
            urgent = request.POST['urgent']
            tckts=Ticket.objects.filter(Q(ticket_status__contains=urgent)).values_list(
            'title', 'customer_email', 'created_date', 'resolved_date', 'resolved_by__email', 'issue_description',)
            if tckts:
                for tckt in tckts:
                    rows.append(tckt)
        if resolved !="":
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
        #load site setups
        setup=System_Settings.objects.first()
        # Modify the content and styles according to the requirement
        page = f"Copyright © {datetime.now().year} {setup.company}. All Rights Reserved. Page {self._pageNumber} of {page_count}"
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

    PAGESIZE = pagesizes.landscape(pagesizes.A4)
    #load site setups
    setup=System_Settings.objects.first()

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
    company = Paragraph(setup.company, styles['Normal_CENTER'])
    suite = Paragraph(setup.suite, styles['Normal_CENTER'])
    road_city_contry = Paragraph(f"{setup.road}-{setup.city},{setup.country}",
                          styles['Normal_CENTER'])
    tel = Paragraph(f"{setup.tel}", styles['Normal_CENTER'])
    email = Paragraph(f"{setup.email}",
                          styles['Normal_CENTER'])
    address = Paragraph(f"P.O Box: {setup.address}", styles['Normal_CENTER'])
    report_title = Paragraph("Ticket Reports as at {}".format(
        datetime.now().strftime("%d-%m-%Y")), styles['Normal_LEFT'])

   
    if setup.logo:
        logo= str(ABSOLUTE_PATH())+str(setup.logo.url)
    else:
        logo = os.path.join(ABSOLUTE_PATH(), "static", "img", "logo.png")
    im = Image(logo, 3 * inch, 1.5 * inch)
    #im.hAlign="LEFT"

    rows = []
    data = []
    data.append(im)
    data.append(company)
    data.append(road_city_contry)
    data.append(suite)
    data.append(email)
    data.append(address)
    data.append(tel)
    data.append(report_title)
    tickets = Ticket.objects.all().order_by("-created_date")  # filter(ticket_status="Resolved")
    headers = ["Ticket Issue", "Status","Raised By","Client Name",
               "Ressolved By", "Date Raised", "Date Ressolved", 
               #"Duration\n(Days:Hrs)"
               ]
    rows.append(headers)
    if request.POST:
        resolved = ""#Resolved
        unsolved = ""
        urgent = ""
        pending = ""
        datefrom = request.POST.get('datefrom','')
        dateto =  request.POST.get('datefrom','')
        cemail = request.POST.getlist('client_mails',['select client'])[0]
        semail = request.POST.getlist('staff_mails',['select staff'])[0]
        if pending !="":
            tickets=tickets.filter(Q(ticket_status=pending))
        if unsolved !="":
            tickets=tickets.filter(Q(ticket_status=unsolved))
        if urgent !="":
            tickets=tickets.filter(Q(ticket_status=urgent))
        if resolved !="":
            tickets=tickets.filter(Q(ticket_status=resolved))
            print(tickets)
        if datefrom != '' and dateto != '':
            tickets=tickets.filter(created_date__range=[datefrom,dateto])
        if semail != 'select staff' or  cemail != 'select client':
            semail = semail[2:-3]
            cemail = cemail[2:-3]
            tickets=tickets.filter(Q(resolved_by__email__contains=semail) | Q(customer_email__contains=cemail))
    tickets=tickets.order_by('-ticket_status')
    for ticket in tickets:
        duration = ""
        issue_description = Paragraph(ticket.issue_description if ticket.issue_description !=None else ticket.tit, styles['BodyText'])
        ticket_status = Paragraph(ticket.ticket_status, styles['BodyText'])
        cemail = Paragraph(ticket.customer_email, styles['BodyText'])
        cname = Paragraph(ticket.customer_full_name, styles['BodyText'])
        semail = [Paragraph(ticket.resolved_by.email, styles['BodyText']) if ticket.resolved_by !=
                  None else "Unknown"][0]
        if ticket.resolved_date != None:
            duration = "D:"+str(abs(ticket.resolved_date-ticket.created_date).days) + \
                " H:"+str("{:.2f}".format((ticket.resolved_date -
                          ticket.created_date).seconds/(3600)))
        else:
            duration = "Unknown"
        rows.append([issue_description,
                     ticket_status,
                     cemail,
                     cname,
                     semail,
                     date_format(ticket.created_date if ticket.created_date is not None else datetime.now(), "SHORT_DATE_FORMAT"),
                     [date_format(ticket.resolved_date if ticket.resolved_date is not None else datetime.now(), "SHORT_DATE_FORMAT")
                      if ticket.resolved_date != None else "Unknown"][0],
                     #duration,
                     ])
    c_width = [4*inch, 0.8*inch,1*inch, 1.5*inch, 1.5*inch, 1.3*inch]
    content_table = Table(rows, colWidths=c_width)
    content_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), ['lightgrey', 'white']),
        ('AUTOSIZE', (0, 0), (-1, -1), True),
        ('AUTOSIZEHEIGHT', (0, 0), (-1, -1), True),
        ('AUTOSETFONTSIZE', (0, 0), (-1, -1), True),
        ('AUTOSETBACKGROUND', (0, 0), (-1, -1), True),
        ('AUTOSETPADDING', (0, 0), (-1, -1), True),
    ]))
    data.append(content_table)

    data.append(PageBreak())
    doc.build(data, canvasmaker=MyCanvas)
    return response
