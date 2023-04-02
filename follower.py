import requests
import json
from collections import defaultdict

# Replace these with your own credentials
client_id = '클라이언트아이디'
client_secret = '클라이언트시크릿'


# Fetch statbots
def get_statbots():
    url = 'https://api.twitchinsights.net/v1/bots/all'
    response = requests.get(url)
    statbots_data = response.json()['bots']
    return set(bot[0].lower() for bot in statbots_data)


# Get OAuth token
def get_oauth_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    return response.json()['access_token']


# Get user ID for a given streamer name
def get_user_data(streamer_name, access_token):
    url = f'https://api.twitch.tv/helix/users?login={streamer_name}'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    user_data = response.json()['data'][0]
    return user_data['id'], user_data['display_name']

# Get chatters list
def get_chatters(streamer_name):
    url = f'https://tmi.twitch.tv/group/user/{streamer_name}/chatters'
    response = requests.get(url)
    chatters_data = response.json()
    chatters = []

    for chatter_type in chatters_data['chatters']:
        chatters.extend(chatters_data['chatters'][chatter_type])

    return chatters


# Get follow date
def get_follow_date(streamer_id, user_id, access_token):
    url = f'https://api.twitch.tv/helix/users/follows?from_id={user_id}&to_id={streamer_id}'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    data = response.json()['data']
    if len(data) > 0:
        return data[0]['followed_at']
    return None


# Main function
def main():
    streamer_name = input('스트리머 ID 입력 : ')
    access_token = get_oauth_token(client_id, client_secret)
    streamer_id, display_name = get_user_data(streamer_name, access_token)
    chatters = get_chatters(streamer_name)
    statbots = get_statbots()

    follow_dates = defaultdict(int)
    follow_dates["Unfollowed"] = 0
    follow_dates["Statbots"] = 0

    for chatter in chatters:
        if chatter.lower() in statbots:
            follow_dates["Statbots"] += 1
            continue

        chatter_id, _ = get_user_data(chatter, access_token)
        follow_date = get_follow_date(streamer_id, chatter_id, access_token)
        if follow_date:
            follow_month = follow_date[:7]
            follow_dates[follow_month] += 1
        else:
            follow_dates["Unfollowed"] += 1

    total_chatters = len(chatters)
    print(f"스트리머: {display_name}")
    print(f"총 시청자수: {total_chatters}")
    print("팔로우 내역")

    for key, count in sorted(follow_dates.items(), key=lambda x: (x[0] not in ["Unfollowed", "Statbots"], x[0])):
        percentage = (count / total_chatters) * 100
        print(f'{key}: {count}명 ({percentage:.2f}%)')

if __name__ == '__main__':
    main()