import pandas as pd
from datetime import datetime
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
from ticketapp.models import Ticket
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication,TokenAuthentication
from rest_framework.parsers import MultiPartParser,FormParser

date_format ='%d/%m/%Y'
class ImportCSVTickets:
    def __init__(self,filepath,request):
        self.filepath=filepath
        self.request=request

    def custom_date_parser(self,date_str):
        if pd.isna(date_str):
           return None
        return datetime.strptime(date_str, date_format)

    def import_tickets(self):
        # Load the CSV file
        tickets_df = pd.read_csv(self.filepath,dtype={'DateResolved': str,'DateRaised':str})
        # tickets_df['DateResolved'] = pd.to_datetime(tickets_df['DateResolved'], format=date_format)
        # tickets_df['DateRaised'] = pd.to_datetime(tickets_df['DateRaised'], format=date_format)
        # Iterate over each row in the DataFrame
        for index, row in tickets_df.iterrows():
            # Extract the data from the row
            title = row['Title']
            issue = row['Issue']
            status = row['Status']
            assignee = row['Asignee'] 
            raised_by = row['RaisedBy']
            date_resolved = row['DateResolved']
            date_raised = row['DateRaised']
            
            # date_resolved = pd.to_datetime(date_resolved,format=date_format) if pd.notna(date_resolved) else None
            # date_raised = pd.to_datetime(date_raised, format=date_format) if pd.notna(date_raised) else None
           
            date_resolved=self.custom_date_parser(date_resolved)
            date_raised=self.custom_date_parser(date_raised)

            # Get the User objects for assignee and raised_by
            try:
                assigned_to_user = User.objects.get(username=assignee)
            except User.DoesNotExist:
                assigned_to_user = None

            try:
                raised_by_user = User.objects.get(email=raised_by)
            except User.DoesNotExist:
                raised_by_user = None

            # Create and save the Ticket object
            ticket,created= Ticket.objects.update_or_create(
                user=self.request.user,
                title=title,
                issue_description=issue,
                ticket_status=status,
                resolved_date=date_resolved,
                created_date=date_raised,
                assigned_to=assigned_to_user,
                resolved_by=assigned_to_user,
                customer_email=raised_by
            )

            # Save the ticket instance
        return "Tickets have been successfully uploaded from the CSV file."

class UploadCSVTicketsData(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    parser_classes = (MultiPartParser, FormParser)  # Add parsers for file upload

    def post(self, request, format=None):
        # Check if the request contains a file
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        file_obj = request.FILES['file']
        # Save the uploaded file
        file_name = default_storage.save(file_obj.name, ContentFile(file_obj.read()))
        # Call the import_employee_data function
        try:
            path=default_storage.path(file_name)
            res=None
            res = ImportCSVTickets(path,request).import_tickets()
            return Response({'message': res}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)