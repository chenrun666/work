# 注入表单

dapDate = req["depDate"].split('-')[1] + "/" + req["depDate"].split('-')[2] + "/" + req["depDate"].split('-')[0]
parameterJS = ''' 
       var searchform=$('<form id="tzSearch" method="post" action ="https://makeabooking.flyscoot.com/"></form>');'''
parameterJS = parameterJS + '''var depInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.SearchStations[0].DepartureStationCode" value="''' + \
              req["depAirport"] + '''"/>');'''
parameterJS = parameterJS + '''searchform.append(depInput);'''
parameterJS = parameterJS + '''var arrInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.SearchStations[0].ArrivalStationCode" value="''' + \
              req["arrAirport"] + '''"/>');'''
parameterJS = parameterJS + '''searchform.append(arrInput);'''
parameterJS = parameterJS + '''var depDateInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.SearchStations[0].DepartureDate" value="''' + dapDate + '''"/>');'''
parameterJS = parameterJS + '''searchform.append(depDateInput);'''
parameterJS = parameterJS + '''var directionInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.Direction" value="Oneway"/>');'''
parameterJS = parameterJS + '''searchform.append(directionInput);'''
parameterJS = parameterJS + '''var adultInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.AdultCount" value="''' + str(
    req["adultNumber"]) + '''"/>');'''
parameterJS = parameterJS + '''searchform.append(adultInput);'''
parameterJS = parameterJS + '''var childInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.ChildrenCount" value="''' + str(
    req["childNumber"]) + '''"/>');'''
parameterJS = parameterJS + '''searchform.append(childInput);'''
parameterJS = parameterJS + '''var infantInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.InfantCount" value="''' + str(
    req["infantNumber"]) + '''"/>');'''
parameterJS = parameterJS + '''searchform.append(infantInput);'''

parameterJS = parameterJS + '''var localeInput = $('<input type="text" name="revAvailabilitySearch.DeepLink.Locale" value=""/>');'''
parameterJS = parameterJS + '''searchform.append(localeInput);'''
parameterJS = parameterJS + '''var organisationCodeInput = $('<input type="text" name="revAvailabilitySearch.DeepLink.OrganisationCode" value=""/>');'''
parameterJS = parameterJS + '''searchform.append(organisationCodeInput);'''
parameterJS = parameterJS + '''var salesCodeInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.SalesCode" value=""/>');'''
parameterJS = parameterJS + '''searchform.append(salesCodeInput);'''
parameterJS = parameterJS + '''var arrivalStationCodeInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.SearchStations[1].ArrivalStationCode" value=""/>');'''
parameterJS = parameterJS + '''searchform.append(arrivalStationCodeInput);'''
parameterJS = parameterJS + '''var departureDateInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.SearchStations[1].DepartureDate" value=""/>');'''
parameterJS = parameterJS + '''searchform.append(departureDateInput);'''
parameterJS = parameterJS + '''var departureStationCodeInput = $('<input type="text" name="revAvailabilitySearch.SearchInfo.SearchStations[1].DepartureStationCode" value=""/>');'''
parameterJS = parameterJS + '''searchform.append(departureStationCodeInput);'''

parameterJS = parameterJS + '''searchform.appendTo('body').submit();'''
logger.info(parameterJS)
browser.execute_script(parameterJS)
