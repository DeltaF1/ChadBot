def onFriendRequest(client, from_id, msg):
    client.friendConnect(from_id)