import PAsearchSites
import PAgenres
import PAactors

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID
    searchString = searchTitle.lower().replace(" ","-")
    Log("searchString: " + searchString)
    url = PAsearchSites.getSearchSearchURL(siteNum) + searchString
    searchResult = HTML.ElementFromURL(url)

    titleString = searchResult.xpath('//title')[0].text_content().replace("FTV Girls","").replace("FTV Milfs","").replace(".com","")
    Log(titleString)
    titleNoFormatting = titleString.split("-")[0].strip()
    curID = url.replace('/','_').replace('?','!')
    subSite = titleString.split("-")[1].strip()
    if searchDate:
        releaseDate = parse(searchDate).strftime('%Y-%m-%d')
    else:
        releaseDate = ''
    score = 100
    results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum) + "|" + releaseDate, name = titleNoFormatting + " [" + subSite + "] " + releaseDate, score = score, lang = lang))

    return results

def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')

    url = str(metadata.id).split("|")[0].replace('_','/').replace('!','?')
    detailsPageElements = HTML.ElementFromURL(url)
    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'FTV'

    # Title
    titleString = detailsPageElements.xpath('//title')[0].text_content().replace("FTV Girls","").replace("FTV Milfs","").replace(".com","")
    actorString = detailsPageElements.xpath('//div[@class="slogan"]/div[2]')[0].text_content().strip()
    metadata.title = titleString.split(actorString)[1].split("-")[0].strip()

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteID).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    if tagline == "FTVGirls":
        for genreName in ["softcore", "glamour", "amateur"]:
            movieGenres.addGenre(genreName)
    elif tagline == "FTVMilfs":
        for genreName in ["amateur", "MILF"]:
            movieGenres.addGenre(genreName)
    else:
        pass

    # Release Date
    date = str(metadata.id).split("|")[2]
    if len(date) > 0:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
        Log("Date from file")

    # Actors
    actors = actorString.split('and')
    for actorLink in actors:
        actorName = actorLink
        actorPhotoURL = ""
        movieActors.addActor(actorName,actorPhotoURL)

    ### Posters and artwork ###

    # Video trailer background image
    try:
        twitterBG = detailsPageElements.xpath('//div[@class="hold"]/video')[0].get('poster')
        art.append(twitterBG)
    except:
        pass

    j = 1
    Log("Artwork found: " + str(len(art)))
    for posterUrl in art:
        if not PAsearchSites.posterAlreadyExists(posterUrl,metadata):            
            #Download image file for analysis
            try:
                img_file = urllib.urlopen(posterUrl)
                im = StringIO(img_file.read())
                resized_image = Image.open(im)
                width, height = resized_image.size
                #Add the image proxy items to the collection
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                j = j + 1
            except:
                pass

    return metadata