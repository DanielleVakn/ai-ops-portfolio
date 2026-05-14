from googleapiclient.errors import HttpError

def run_organizer(service, gmail_query, label_name):
    print(f"Agent 1: Organizing emails into '{label_name}' for query '{gmail_query}'")
    try:
        # Create label if it doesn't exist
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        label_id = None
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
                
        if not label_id:
            print(f"Creating label: {label_name}")
            label_object = {'name': label_name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
            created_label = service.users().labels().create(userId='me', body=label_object).execute()
            label_id = created_label['id']
            
        # Search for messages with pagination
        messages = []
        page_token = None
        while True:
            results = service.users().messages().list(userId='me', q=gmail_query, pageToken=page_token).execute()
            if 'messages' in results:
                messages.extend(results['messages'])
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        if not messages:
            print("No matching emails found.")
            return

        print(f"Found {len(messages)} matching emails. Applying label...")
        
        # Batch modify in chunks of 1000 (Gmail API limit)
        message_ids = [msg['id'] for msg in messages]
        for i in range(0, len(message_ids), 1000):
            chunk = message_ids[i:i+1000]
            body = {
                'ids': chunk,
                'addLabelIds': [label_id],
                'removeLabelIds': []
            }
            service.users().messages().batchModify(userId='me', body=body).execute()
        
        print(f"Successfully labeled {len(messages)} emails as '{label_name}'.")
        
    except HttpError as error:
        print(f"An error occurred: {error}")
