from googleapiclient.errors import HttpError

def run_cleaner(service, gmail_query):
    print(f"Agent 2: Finding and deleting emails for query '{gmail_query}'")
    deleted_subjects = []
    try:
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
            print("No matching emails found to delete.")
            return []

        print(f"Found {len(messages)} matching emails. Gathering subjects and deleting...")
        
        message_ids = []
        for idx, msg in enumerate(messages):
            msg_id = msg['id']
            message_ids.append(msg_id)
            
            # Fetch message to get subject (limit to 100 subjects to avoid huge API delays if large)
            if idx < 100:
                msg_details = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['Subject']).execute()
                headers = msg_details.get('payload', {}).get('headers', [])
                subject = "No Subject"
                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                deleted_subjects.append(subject)
            elif idx == 100:
                deleted_subjects.append(f"... and {len(messages) - 100} more emails (subject extraction capped for speed)")
            
        # Trash messages directly using batchModify (chunked per 1000)
        for i in range(0, len(message_ids), 1000):
            chunk = message_ids[i:i+1000]
            body = {
                'ids': chunk,
                'addLabelIds': ['TRASH'],
                'removeLabelIds': ['INBOX']
            }
            service.users().messages().batchModify(userId='me', body=body).execute()
        
        print("\nEmails deleted (moved to Trash). Subjects:")
        for idx, subj in enumerate(deleted_subjects, 1):
            if idx <= 100:
                print(f"{idx}. {subj}")
            else:
                print(subj)
            
        return deleted_subjects

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
