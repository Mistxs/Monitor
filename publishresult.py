import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

def publishresult(data):
    CREDENTIALS_FILE = 'key.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    spreadsheetId = "1Sv0jYXu0hLBNqvpJT0Fy2rU3MIQyI0Q6obV3D8JzdBU"
    print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)

    # driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
    # access = driveService.permissions().create(
    #     fileId=spreadsheetId,
    #     body={'type': 'user', 'role': 'writer', 'emailAddress': 'filippovanatoliy@gmail.com'},
    #     fields='id'
    # ).execute()

    values = []
    for item in data:
        row_values = [item["date"], item.get("Status", "")]
        errors = item.get("Errors", [])
        if errors:
            for i, error in enumerate(errors):
                error_link = error.get("Link", "")
                error_status = error.get("ExecutionStatus", "")
                if i == 0:
                    values.append(row_values + [error_link, error_status])
                else:
                    values.append(["", "", error_link, error_status])
        else:
            values.append(row_values + ["", ""])

    range_name = "Sheet1!A3:D"
    body = {"values": values}
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId, range=range_name, valueInputOption="USER_ENTERED", insertDataOption='INSERT_ROWS', body=body
    ).execute()

    print("Данные успешно записаны в таблицу.")
