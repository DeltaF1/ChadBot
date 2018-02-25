
def parse_message(client, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg):
    print("Inside module!")
    if message_object.text.lower() == "testing_modules":
        print("Sending!")
        return client.type_message("SENT FROM A MODULE", thread_id, thread_type)