from data.get_from_wookiepedia import TimelineCannonMedia

if __name__ == '__main__':

    wookiepedia_timeline = TimelineCannonMedia()
    print(wookiepedia_timeline.read_in_data())
