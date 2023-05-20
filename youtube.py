from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from editVideo import downloadVideo, cutVideo
import requests
import os

youtube = build('youtube', 'v3', developerKey='AIzaSyAcXNUDQGgOPa7bHRJYeaa89Ick55GWZPE')

def isIdNotInFile(file, videoId):
    with open(file, 'r') as file:
        for line in file:
            if line.strip() == videoId:
                return False
    return True

async def search(ctx, query, nextPageToken=None):
    try:
        channel_id = None
        segments = query.split("/")
        if channel_name := next(
            (segment[1:] for segment in segments if segment.startswith("@")),
            None,
        ):
            request = youtube.search().list(
                part='snippet',
                maxResults=50,
                order='viewCount',
                pageToken=nextPageToken,
                type="channel",
                q=channel_name,
            )
            response = request.execute()
            allVideos = response['items']
            channel_id = allVideos[0]['id']['channelId']
            search = None
        else:
            search = query

        request = youtube.search().list(
            part='snippet',
            type='video',
            maxResults=50,
            order='viewCount',
            pageToken=nextPageToken,
            q=search,
            channelId=channel_id
        )
        response = request.execute()

        allVideos = response['items']
        if len(allVideos):
            for index, video in enumerate(allVideos):
                videoId = video['id']['videoId']
                mostReplayed = getMostReplayed(videoId)
                if isIdNotInFile('videoAlreadyExported.txt', videoId) and mostReplayed and len(mostReplayed['heatMarkers']):
                    print(f'{index} ==> most replayed found !!')
                    formatedMostReplayed = formatMostReplayed(mostReplayed['heatMarkers'])
                    file_path = downloadVideo(f"https://www.youtube.com/watch?v={videoId}")
                    await cutVideo(ctx, file_path, formatedMostReplayed)
                    os.remove(file_path)
                    with open('videoAlreadyExported.txt', 'a') as f:
                        f.write(videoId)
                        f.write('\n')
                    return
                print(f'{index}: No most replayed found')
            if response['nextPageToken']:
              await search(ctx, query, response['nextPageToken'])  # Appel récursif avec nextPageToken

    except Exception as e:
        print('search_yt => Une erreur s\'est produite:', e)
        return None


def getMostReplayed(videoId):
    try:
        url = "https://yt.lemnoslife.com/videos"
        params = {
            "part": "mostReplayed",
            "id": videoId
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data['items']
            if items and len(items) and items[0]['mostReplayed']:
                return items[0]['mostReplayed']
        else:
            print("getMostReplayed => La requête a échoué avec le code d'erreur :", response.status_code)
    except Exception as e:
      print('getMostReplayed => Une erreur s\'est produite:', e)
      return None

def formatMostReplayed(array):
    try:
        filteredArray = list(filter(lambda x: x['heatMarkerRenderer']['heatMarkerIntensityScoreNormalized'] > 0.35, array))
        resultat = []
        for element in filteredArray:
            start = element['heatMarkerRenderer']['timeRangeStartMillis']
            end = start + element['heatMarkerRenderer']['markerDurationMillis']
            startCopy = start
            endCopy = end
            if startCopy > 0 and startCopy > 40000:
                startCopy -= 40000
            endCopy = end + 40000
            if len(resultat) and (startCopy >= resultat[-1]['start'] and startCopy <= resultat[-1]['end']) :
                resultat[-1]['end'] = endCopy
            else:
                resultat.append({'start': startCopy, 'end': endCopy})
        print(resultat)
        return resultat

    except Exception as e:
      print('formatMostReplayed => Une erreur s\'est produite:', e)
      return None
