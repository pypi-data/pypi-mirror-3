# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import json
import os
import operator

from trosnoth.data import getPath, makeDirs
from trosnoth.utils.utils import hasher
from trosnoth.data import statGeneration
from trosnoth.gamerecording.achievementlist import (leaderAchievements,
        additionalLeaders, stripPunctuation)

def generateHtml(htmlPath, statPath):

    def plural(value):
        if value == 1:
            return ""
        else:
            return "s"

    def add(value, statName=None, altText=None, spacing=True, className=None):
        if altText is not None:
            points = pointValues[altText] * value
            if type(points) == float:
                points = '%2.2f' % points
            altText = ' title="%s point%s\"' % (points, plural(points))
        else:
            altText = ''

        if className is not None:
            classText = ' class="%s"' % (className)
        else:
            classText = ''

        if type(value) == float:
            value = '%2.2f' % value

        if statName is None:
            html.append("\t\t\t\t<td%s%s>%s</td>" % (altText, classText, value))
        else:
            nbsp = ""
            if spacing is False:
                pluralStr = ""
            else:
                nbsp = "&nbsp;"
                pluralStr = plural(value)
            html.append("\t\t\t\t<td%s>%s%s%s%s</td>" % (altText, value, nbsp,
                    statName, pluralStr))

    def addList(title, data):
        html.append("\t\t\t\t\t<li><b>%s:</b> " % title)

        if len(data) == 0:
            html.append("\t\t\t\t\t\tNone")
        else:
            data = sorted(data.iteritems(), key=operator.itemgetter(1),
                    reverse=True)
            string = []
            for details in data:
                string.append("%s (%d)" % details)
            html.append("\t\t\t\t\t\t" + ", ".join(string))

        html.append("\t\t\t\t\t</li>")

    def accuracy(shotsHit, shotsFired):
        try:
            return ((shotsHit ** 2) / (shotsFired + 0.0)) * 30
        except ZeroDivisionError:
            return 0

    from trosnoth.gamerecording.gamerecorder import statDir

    makeDirs(statDir)

    if statPath == '':
        files = os.listdir(statDir)
    else:
        files = [statPath]

    playerStats = {}
    statNames = ['aliveStreak', 'deaths', 'killStreak', 'kills', 'roundsLost',
            'roundsWon', 'shotsFired', 'shotsHit', 'starsEarned', 'starsUsed',
            'starsWasted', 'tagStreak', 'timeAlive', 'timeDead', 'zoneAssists',
            'zoneTags']
    statEnemies = ['playerDeaths', 'playerKills', 'upgradesUsed']
    pointValues = {'kills': 10, 'deaths': 1, 'zoneTags': 20, 'accuracy': 20,
            'starsUsed': 3, 'zoneAssists': 5}
    leaders = map(str.lower, leaderAchievements.keys() +
            additionalLeaders.keys())

    tableHeaders = [
        ['#', 'Nick', 'Kills', 'Deaths', 'KDR', 'Zone Tags', 'Shots Fired',
            'Shots Hit', 'Accuracy', 'Stars Used', 'Killed the most:',
            'Died the most to:', 'Points'],
        ['#', 'Nick', 'Stars Earned', 'Stars Used', 'Stars Wasted',
                'Favourite Upgrade', 'Time Alive', 'Time Dead', 'ADR',
                'Longest Life', 'Points'],
        ['#', 'Nick', 'Kills', 'Kill Streak', 'Zone Tags', 'Zone Assists',
                'Tag Streak', 'Points'],
    ]

    tableNames = ['General Overview', 'Stars and Time', 'Kills and Tags']

    for x in range(0, len(tableNames)):
        style = ""
        if x == 0:
            style = " style='color: black;'"
        tableNames[x] = ('<span class="name topLink" id="link%s" '
                'onClick="navigate(\'%s\', %d)"%s>%s</span>' %
                (x, x, len(tableHeaders[x]), style, tableNames[x]))

    navigation = " &ndash; ".join(tableNames)

    html = []
    fileMatrix = {}

    for filename in files:

        if filename[-9:] != ".trosstat":
            filename = filename + ".trosstat"
        statLocation = os.path.join(statPath, filename)

        try:
            statFile = open(statLocation)
        except IOError:
            raise Exception("'%s' does not exist!" % filename)

        loadedStats = json.load(statFile)

        for nick in loadedStats['players']:
            if nick not in playerStats:
                playerStats[nick] = loadedStats['players'][nick]
                fileMatrix[nick] = [filename]
            else:
                for stat in statNames:
                    playerStats[nick][stat] += (
                            loadedStats['players'][nick][stat])
                for stat in statEnemies:
                    for enemy in loadedStats['players'][nick][stat]:
                        if enemy not in playerStats[nick][stat]:
                            playerStats[nick][stat][enemy] = 0
                        playerStats[nick][stat][enemy] += (
                                loadedStats['players'][nick][stat][enemy])
                fileMatrix[nick].append(filename)

    ranking = {}
    allData = {}

    for nick in playerStats:
        data = playerStats[nick]
        try:
            data['accuracy'] = (100.0 * data['shotsHit']) / data['shotsFired']
        except ZeroDivisionError:
            data['accuracy'] = 0

        for stat in statEnemies:
            data[stat + "Full"] = data[stat].copy()
            highest = 0
            highestName = "----"
            names = data[stat]
            for k, v in names.items():
                if v > highest:
                    highest = v
                    highestName = k
            if highest == 0:
                data[stat] = highestName
            else:
                data[stat] = "%s (%s)" % (highestName, highest)

        data['score'] = 0
        for stat, value in pointValues.items():
            points = data[stat] * value
            data['score'] += points

        try:
            data['kdr'] = '%2.2f' % (float(data['kills']) / data['deaths'])
        except ZeroDivisionError:
            data['kdr'] = "----"

        try:
            data['adr'] = '%2.2f' % (float(data['timeAlive']) /
                    data['timeDead'])
        except ZeroDivisionError:
            data['adr'] = "----"

        ranking[nick] = data['score']
        allData[nick] = data

    rankingList = sorted(ranking.iteritems(), key=operator.itemgetter(1),
            reverse=True)
    ranking = {}

    rankCount = 0

    html.append("\t\t<table class='ladder'>");

    for count in range(0, len(tableNames)):
        style = ""
        if count != 0:
            style = " style='display: none;'"
        html.append("\t\t\t<tr class='allRows group%s'%s>" % (count, style))
        for caption in tableHeaders[count]:
            html.append("\t\t\t\t<th>%s</th>" % caption)
        html.append("\t\t\t</tr>")

    teamNames = ('Blue', 'Red')
    if loadedStats.has_key('winningTeamId'):
        winningTeamId = loadedStats['winningTeamId']
        if winningTeamId == 'A':
            winText = '%s Team won' % (teamNames[0],)
            colour = 'navy'
        elif winningTeamId == 'B':
            winText = '%s Team won' % (teamNames[1],)
            colour = 'maroon'
        else:
            winText = 'Game was a draw'
            colour = 'green'
    else:
        winText = 'Game was not finished'
        colour = 'gray'

    html.append('<p class="wintext" style="color: %s;">%s</p>' % (colour,
            winText))
    for pair in rankingList:

        nick = pair[0]
        rankCount += 1
        rankStr = str(rankCount)

        classy = ""
        if stripPunctuation(nick).lower() in leaders:
            classy = " leader";
            rankCount -= 1
            rankStr = '--'

        data = allData[nick]

        if data['bot']:
            classy = " bot";
            rankCount -= 1
            rankStr = 'B'

        nickHash = hasher(nick).hexdigest()

        for count in range(0, len(tableNames)):

            style = ""
            if count != 0:
                style = " style='display: none;'"

            html.append("\t\t\t<tr class='allRows group%s%s'%s>" % (count,
                    classy, style))
            if (data['team'] == 'A'):
                bgColour='blueteam'
            elif (data['team'] == 'B'):
                bgColour='redteam'
            elif (data['team'] == '\x00'):
                bgColour='rogue'
            add('<strong>%s</strong>' % rankStr, className=bgColour)
            add('<span class="name" onClick="toggle(\'details-%s\')">%s</span>'
                    % (nickHash, nick))

            if count == 0:
                add(data['kills'], 'kill', 'kills')
                add(data['deaths'], 'death', 'deaths')
                add(data['kdr'])
                add(data['zoneTags'], 'tag', 'zoneTags')
                add(data['shotsFired'], 'shot')
                add(data['shotsHit'], 'shot')
                add(data['accuracy'], '%', 'accuracy', False)
                add(data['starsUsed'], 'star', 'starsUsed')
                add(data['playerKills'])
                add(data['playerDeaths'])
            elif count == 1:
                add(data['starsEarned'], 'star')
                add(data['starsUsed'], 'star', 'starsUsed')
                add(data['starsWasted'], 'star')
                add(data['upgradesUsed'])
                add(int(data['timeAlive']), 'second')
                add(int(data['timeDead']), 'second')
                add(data['adr'])
                add(int(data['aliveStreak']), 'second')
            elif count == 2:
                add(data['kills'], 'kill', 'kills')
                add(data['killStreak'], 'kill')
                add(data['zoneTags'], 'tag', 'zoneTags')
                add(data['zoneAssists'], 'assist', 'zoneAssists')
                add(data['tagStreak'], 'zone')
            elif count == 3:
                add(data['shotsFired'], 'shot')
                add(data['shotsHit'], 'shot')
                add(data['accuracy'], '%', spacing = False)
                old = data['accuracy'] * 20
                new = accuracy(data['shotsHit'], data['shotsFired'])
                add(old, 'point')
                add(new, 'point')
                add(new - old)

            add('<strong>%2.2f</strong>' % data['score'])
            html.append("\t\t\t</tr>")

            if count == len(tableNames) - 1:
                html.append("\t\t\t<tr id='details-%s' style='display: none;'>"
                        % nickHash)
                html.append("\t\t\t\t<td colspan='%d' class='details'"
                        "style='text-align: left;'>" % len(tableHeaders[0]))
                html.append("\t\t\t\t\t<ul>")

                addList("Players killed", data['playerKillsFull'])
                addList("Players died to", data['playerDeathsFull'])
                addList("Upgrades used", data['upgradesUsedFull'])

                html.append("\t\t\t\t\t</ul>")
                html.append("\t\t\t\t</td>")
                html.append("\t\t\t</tr>")

    html.append("\t\t</table>")

    html = "\n" + "\n".join(html) + "\n"

    baseHTML = open(getPath(statGeneration, 'statGenerationBase.htm'),
            'r').read()

    html = baseHTML.replace("[[TABLE]]", html)
    html = html.replace("[[NAVIGATION]]", navigation)

    htmlFile = open(htmlPath, "w")
    htmlFile.write(html)
    htmlFile.flush()
    htmlFile.close()
