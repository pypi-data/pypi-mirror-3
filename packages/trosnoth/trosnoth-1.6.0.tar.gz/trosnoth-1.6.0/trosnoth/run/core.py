import cgi
import logging
from optparse import OptionParser
import os
import subprocess
import sys
import urllib
import webbrowser

import pygame.display
from twisted.web import server
from twisted.internet import reactor
from twisted.internet.error import CannotListenError

from trosnoth import data
import trosnoth.data.startupMenu
from trosnoth.gui.app import Application
from trosnoth.gui.common import Location, NewImage
from trosnoth.gui.fonts.font import Font
from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import (TextElement, PictureElement,
        TextButton)
from trosnoth.network.networkDefines import validServerVersions
from trosnoth.settings import (ConnectionSettings, DisplaySettings,
        SoundSettings)
from trosnoth.utils.utils import initLogging
from trosnoth.version import titleVersion, fullVersion
from trosnoth.web.site import PageSet, ServerState, Resources, Template

log = logging.getLogger('core')

core = PageSet()

DOCTYPE = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" '
        '"http://www.w3.org/TR/html4/loose.dtd">')

pageTemplate = Template('''%(docType)s
<html>
<head>
<title>%(title)s</title>
<link href="/style.css" rel="stylesheet" type="text/css">
%(headers)s
</head>
<body>
<div id="container">
  %(contents)s
  %(backbtn)s
  <div id="version_text">%(version)s</div>
</div>
</body>
</html>''',
{
    'docType': DOCTYPE,
    'title': 'Trosnoth',
    'headers': '',
    'contents': '',
    'backbtn': '<div id="menu_back_btn"><a href="/">back</a></div>',
    'version': cgi.escape(titleVersion),
})

@core.addPage('/')
def home(state, request):
    return pageTemplate.apply(headers='''
<script type="text/javascript">
function practise() {
  if (window.XMLHttpRequest) {
      xmlhttp = new XMLHttpRequest();
  } else {
    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
  }
  xmlhttp.open('GET', '/ajax/practise', true);
  xmlhttp.send();
}
</script>''', contents='''
  <div id="home_play_btn"><a href="/play">play</a></div>
  <div id="home_practise_btn"><a href="/practise"
    onclick="practise(); return false;">practise</a></div>
  <div id="home_archives_btn"><a href="/archives">archives</a></div>
  <div id="home_settings_btn"><a href="/settings">settings</a></div>
  <div id="home_credits_btn"><a href="/credits">credits</a></div>
  <div id="home_exit_btn"><a href="/shutdown">exit</a></div>
''', backbtn='')

@core.addPage('/data/background')
def background(state, request):
    request.setHeader('Content-Type', 'image/png')
    if not hasattr(background, '_cachedImage'):
        background._cachedImage = open(data.getPath(data,
                'startupMenu', 'blackdrop.png'), 'rb').read()
    return background._cachedImage

@core.addPage('/style.css')
def style(state, request):
    request.setHeader('Content-Type', 'text/css')
    return '''
#home_play_btn a,
#home_play_special_btn a,
#home_practise_btn a,
#home_archives_btn a,
#home_settings_btn a,
#home_credits_btn a,
#home_exit_btn a,
#menu_back_btn a,
.central_message,
.prompt,
.option a
{
  color: #000060;
  text-decoration: none;
  font-family: Junction, Verdana, Helvetica, sans-serif;
  font-size: 36px;
  position: absolute;
}

#home_play_btn a {
  font-size: 54px;
  left: 65px;
  top: 225px;
}

.central_message,
.prompt
{
  text-shadow: #c0c0c0 1px 1px 1px;
}

.central_message,
.prompt,
.option a
{
  width: 1024px;
  text-align: center;
  position: absolute;
  font-size: 30px;
}
.central_message
{
  top: 225px;
  width: 924px;
  padding: 0 50px;
}
.prompt { top: 150px; }

#home_play_special_btn a,
#home_practise_btn a
{
  font-size: 30px;
}

#home_play_special_btn a { left: 85px; top: 285px; }
#home_practise_btn a { left: 85px; top: 325px; }
#home_archives_btn a { left: 65px; top: 430px; }
#home_settings_btn a { left: 65px; top: 500px; }
#home_credits_btn a { left: 65px; top: 570px; }
#home_exit_btn a { right: 48px; top: 670px; }
#menu_back_btn a { right: 48px; top: 670px; }

#home_play_btn a:hover,
#home_play_special_btn a:hover,
#home_practise_btn a:hover,
#home_archives_btn a:hover,
#home_settings_btn a:hover,
#home_credits_btn a:hover,
#home_exit_btn a:hover,
#menu_back_btn a:hover,
.option a:hover
{
  color: #8080c0;
}

#credits {
  position: absolute;
  left: 50px;
  top: 130px;
  right: 50px;
  bottom: 90px;
  white-space: pre-wrap;
  color: #000060;
  text-align: center;
  text-shadow: #c0c0c0 1px 1px 1px;
  font-size: 24px;
  font-family: Junction, Verdana, Helvetica, sans-serif;
  overflow: hidden;
}
#credits h1 {
  font-size: 48px;
  font-family: "Lucida Console", Monaco, monospace;
  margin-bottom: -30px;
}
#credits h2 {
  font-size: 36px;
  font-family: "Lucida Console", Monaco, monospace;
  margin-bottom: -20px;
}
#settings_box h1 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-family: Junction, Verdana, Helvetica, sans-serif;
  font-size: 30px;
}
#status {
  font-family: Junction, Verdana, Helvetica, sans-serif;
  font-size: 18px;
  text-align: center;
  background-color: #ffddaa;
}

#version_text {
  font-size: 16px;
  font-family: Junction, Verdana, Helvetica, sans-serif;
  color: #808080;
  position: fixed;
  right: 5px;
  bottom: 0px;
}

#container {
  max-width: 1024px;
  height: 768px;
  margin: 0 auto;
  background-image: url('/data/background');
  position: relative;
}

#settings_box {
  width: 904px;
  margin: 0 50px;
  background: rgb(0, 40, 0);
  background: rgba(128, 180, 128, 0.75);
  position: absolute;
  top: 140px;
  min-height: 520px;
  padding: 0px 10px;
}
'''

@core.addPage('/play')
def play(state, request):
    if 'server' in request.args:
        server = request.args['server'][0]
        port = request.args.get('port', ['6787'])[0]
        try:
            port = int(port)
        except ValueError:
            return message('%r is not a valid port' % (port,),
                    'Trosnoth :: Invalid port')

        if 'version' in request.args:
            if request.args['version'][0] not in validServerVersions:
                return message('%r is running incompatible Trosnoth '
                        'version %s' % (server, request.args['version'][0]),
                        'Trosnoth :: Incompatible server version')

        returnUrl = request.args.get('returnurl', ['/'])[0]
        force = request.args.get('force', [''])[0] == state.uuid.hex
        if state.isServerKnown(server, port) or force:
            # Connect to server.
            state.playGame(server, port)
            request.setResponseCode(302)
            request.setHeader('Location', returnUrl)
            return message('Game launched.', 'Trosnoth :: Play')
        else:
            return prompt(
                'Trosnoth :: Unknown server',
                '%s:%s is not a known server.' % (server, port),
                [
                    ('Play anyway',
                        '/play?server=%s;port=%d;force=%s;returnurl=%s' % (
                        server, port, state.uuid.hex, urllib.quote(returnUrl))),
                    ('Add to known servers',
                        '/addserver?server=%s;port=%d;uuid=%s;returnurl=%s' %
                        (server, port, state.uuid.hex,
                            urllib.quote(returnUrl))),
                    ('Cancel', '/'),
                ]
            )

    launchPlayMenu(state)
    request.setResponseCode(302)
    request.setHeader('Location', '/')
    return message('Play screen launched.', 'Trosnoth :: Play')

@core.addPage('/addserver')
def addServer(state, request):
    uuid = request.args.get('uuid', [''])[0]
    if uuid != state.uuid.hex:
        return message('Invalid request', 'Trosnoth :: Invalid request')

    try:
        server = request.args['server'][0]
        port = int(request.args['port'][0])
    except (KeyError, IndexError, TypeError):
        return message('Invalid request', 'Trosnoth :: Invalid request')

    returnUrl = request.args.get('returnurl', ['/'])[0]
    state.addServer(server, port, '' if returnUrl == '/' else returnUrl)
    return prompt('Trosnoth :: Server added',
        '%s:%s added to known servers' % (server, port),
        [
            ('Play now', '/play?server=%s;port=%d;returnurl=%s' %
                    (server, port, urllib.quote(returnUrl))),
            ('Visit %s' % (cgi.escape(returnUrl),), returnUrl),
            ('Return to menu', '/'),
        ]
    )

def prompt(title, msg, options):
    optionLines = []

    if len(options) > 1:
        interval = min(100, int(350. / (len(options) - 1)))
        start = 225 + int((350 - interval * (len(options) - 1)) / 2)
    else:
        interval = 100
        start = 400

    tops = [start + i * interval for i in xrange(len(options))]
    for option, url in options:
        top = tops.pop(0)
        optionLines.append('<div class="option">'
                '<a style="top: %spx;" href="%s">%s</a></div>' % (
                top, url, cgi.escape(option)))
    return pageTemplate.apply(title=cgi.escape(str(title)), contents='''
  <div class="prompt">%(message)s</div>
  %(options)s''' % {
    'message': cgi.escape(str(msg)),
    'options': '\n'.join(optionLines),
})

def getInt(args, key, default):
    if key not in args:
        return default
    try:
        return int(args[key][0])
    except ValueError:
        return default

@core.addPage('/settings')
def settings(state, request):
    setHash = ''
    savedMsg = ''
    if request.method == 'POST':
        if 'page' in request.args:
            setHash = 'window.location.hash = %r;' % (request.args['page'][0],)

        fullScreen = getInt(request.args, 'fullscreen',
                state.displaySettings.fullScreen)
        state.displaySettings.fullScreen = bool(fullScreen)

        xRes = getInt(request.args, 'xres', state.displaySettings.size[0])
        yRes = getInt(request.args, 'yres', state.displaySettings.size[1])
        state.displaySettings.size = (xRes, yRes)
        state.displaySettings.useAlpha = 'alpha' in request.args
        state.displaySettings.smoothPanning = 'smoothpan' in request.args
        state.displaySettings.windowsTranslucent = ('clearwindows' in
                request.args)
        state.displaySettings.centreOnPlayer = ('playercentre' in request.args)

        state.soundSettings.musicEnabled = 'music' in request.args
        state.soundSettings.musicVolume = getInt(request.args, 'musicvol',
                state.soundSettings.musicVolume)
        state.soundSettings.soundEnabled = 'sound' in request.args
        state.soundSettings.soundVolume = getInt(request.args, 'soundvol',
                state.soundSettings.soundVolume)

        if 'resolution' in request.args:
            res = request.args['resolution'][0]
            if 'x' in res:
                x, y = res.split('x', 1)
                try:
                    x = int(x)
                    y = int(y)
                except ValueError:
                    pass
                else:
                    if (x, y) in pygame.display.list_modes():
                        state.displaySettings.fsSize = (x, y)

        servers = []
        deletions = set()
        serverNames = request.args.get('serverName', [])
        serverPorts = request.args.get('serverPort', [])
        serverSites = request.args.get('serverSite', [])
        for i in xrange(min(len(serverNames), len(serverPorts))):
            server = serverNames[i]
            website = serverSites[i] if i < len(serverSites) else ''
            try:
                port = int(serverPorts[i])
            except ValueError:
                try:
                    server, port, website = state.connectionSettings.servers[i]
                except IndexError:
                    server, port, website = '', 0, ''
            if not server:
                deletions.add(i)
            servers.append((server, port, website))

        for k in request.args:
            if k.startswith('serverDel'):
                try:
                    deletions.add(int(k[len('serverDel'):]))
                except ValueError:
                    pass
        for i in sorted(deletions, reverse=True):
            if len(servers) > i:
                servers.pop(i)
        state.connectionSettings.servers = servers
        state.connectionSettings.otherGames = 'otherGames' in request.args
        lanGames = request.args.get('lanGames', [None])[0]
        if lanGames in ('never', 'afterInet', 'beforeInet'):
            state.connectionSettings.lanGames = lanGames
        state.connectionSettings.createGames = 'createGames' in request.args

        state.displaySettings.save()
        state.soundSettings.save()
        state.connectionSettings.save()
        savedMsg = 'setStatus("Settings saved.");'

    resolutions = []
    for x, y in pygame.display.list_modes():
        resolutions.append('<option value="%(x)dx%(y)d" %(sel)s>%(x)d x %(y)d'
                '</option>' % {
            'x': x,
            'y': y,
            'sel': 'selected="1"' if (x, y) == state.displaySettings.fsSize
                else '',
        })

    servers = []
    i = 0
    for host, port, website in state.connectionSettings.servers:
        servers.append('''
        <tr>
          <td><input type="checkbox" name="serverDel%(i)d"></td>
          <td><input type="text" size="20" name="serverName" value="%(host)s">
            </td>
          <td><input type="text" size="4" name="serverPort" value="%(port)s">
            </td>
          <td><input type="text" size="20" name="serverSite" value="%(site)s">
            </td>
          <td><a href="%(siteUrl)s" target="_blank">%(site)s</a></td>
        </tr>''' % {
            'host': cgi.escape(host),
            'port': cgi.escape(str(port)),
            'site': cgi.escape(website),
            'siteUrl': website,
            'i': i,
        })
        i += 1
    serverList = '''
    <table>
    <tr><th>Del</th><th>Server</th><th>Port</th><th>Website</th><th>Go (new
      window)</th></tr>
    %s
    <tr>
      <td></td>
      <td><input type="text" size="20" name="serverName" value=""></td>
      <td><input type="text" size="4" name="serverPort" value=""></td>
      <td><input type="text" size="20" name="serverSite" value=""></td>
      <td></td>
    </tr>
    </table>
    ''' % ('\n'.join(servers),)

    return pageTemplate.apply(title='Trosnoth :: Settings', headers='''
<style type="text/css">
  .settings_tab {
    display: none;
    margin-top: 15px;
    margin-left: 15px;
    line-height: 3.5;
  }
  .settings_tab table,
  .settings_tab h2
  {
    line-height: 1;
  }
  .selected { display: block; }
  .settings_tab h1 { display: none; }
  .tab_header {
    border-bottom: 1px solid black;
    padding-bottom: 15px;
    padding-top: 15px;
  }
  .tab_header a {
    border: 1px solid grey;
    color: #006000;
    font-family: Junction, Verdana, Helvetica, sans-serif;
    font-size: 36px;
    margin: 5px;
    padding: 5px;
    text-decoration: none;
  }
  .tab_header a.highlighted { color: #ffffff; }
  .tab_header a:hover { color: #c0ffc0; }
</style>
<noscript>
  <style type="text/css">
    .settings_tab {
      display: block;
      line-height: 1;
      margin-left: 0;
    }
    .settings_tab h1 { display: block; }
    .tab_header { display: none; }
  </style>
</noscript>
<script type="text/javascript">
  var lastHash;
  function showElements(elementId) {
    var i;
    var elements = document.getElementsByClassName("selected");
    for (i = 0; i < elements.length; i++) {
      elements[i].className = "settings_tab";
    };

    elements = document.getElementsByClassName("highlighted");
    for (i = 0; i < elements.length; i++) {
      elements[i].className = "";
    };

    document.getElementById(elementId + 'Tab').className = \
        "settings_tab selected";
    document.getElementById(elementId + 'Link').className = "highlighted";
    lastHash = window.location.hash;
    document.getElementById("pageinput").value = lastHash;
  }
  function switchTo(hash) {
    window.location.hash = hash;
    checkHash();
  }
  function checkHash() {
    if (window.location.hash != lastHash) {
      if (window.location.hash == "") {
        showElements("display");
      } else {
        showElements(window.location.hash.substring(1));
      }
    }
  }
  var statusTimeout;
  function setStatus(msg) {
    if (statusTimeout) {
        clearTimeout(statusTimeout);
    }
    document.getElementById("status").innerHTML = msg;
    document.getElementById("status").style.display = "block";
    statusTimeout = setInterval(hideStatus, 5000);
  }
  function hideStatus(msg) {
    document.getElementById("status").style.display = "none";
    statusTimeout = null;
  }
  function keySettings() {
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    } else {
      xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.open('GET', '/ajax/keysettings', true);
    xmlhttp.send();
  }
</script>
''', contents='''
  <div id="status" style="display:none;"></div>
  <div id="settings_box">
    <form method="POST">
      <div class="tab_header">
        <a href="#display" onclick="switchTo('display'); return false;"
          id="displayLink">Display</a>
        <a href="#controls" onclick="switchTo('controls'); return false;"
          id="controlsLink">Controls</a>
        <a href="#sounds" onclick="switchTo('sounds'); return false;"
          id="soundsLink">Sounds</a>
        <a href="#servers" onclick="switchTo('servers'); return false;"
          id="serversLink">Servers</a>
      </div>
      <div class="settings_tab" id="displayTab">
        <h1>Display</h1>
        <input type="radio" name="fullscreen" value="0" id="windowed"
          %(windowed)s>
        <label for="windowed">Display in window</label>,
        <label for="xres">with resolution</label>
        <input type="text" name="xres" id="xres" size="4" value="%(xres)s"> x
        <input type="text" name="yres" size="4" value="%(yres)s"><br>

        <input type="radio" name="fullscreen" value="1" id="fullscreen"
          %(fullscreen)s>
        <label for="fullscreen">Display fullscreen</label>,
        <label for="resolution"> with resolution</label>
        <select name="resolution" id="resolution">
          %(resolutions)s
        </select><br>

        <input type="checkbox" name="alpha" id="alpha" %(alpha)s> <label
          for="alpha">Use alpha channel</label><br>
        <input type="checkbox" name="clearwindows" id="clearwindows"
          %(clearwindows)s>
        <label for="clearwindows">Translucent windows</label><br>
        <input type="checkbox" name="smoothpan" id="smoothpan" %(smoothpan)s>
        <label for="smoothpan">Smooth panning</label><br>
        <input type="checkbox" name="playercentre" id="playercentre"
          %(playercentre)s>
        <label for="playercentre">Centre on player</label><br>
      </div>
      <div class="settings_tab" id="controlsTab">
        <h1>Controls</h1>
        <a href="/settings/controls"
          onclick="keySettings(); return false;">Change controls</a><br>
      </div>
      <div class="settings_tab" id="soundsTab">
        <h1>Sounds</h1>
        <input type="checkbox" name="music" id="music" %(music)s>
        <label for="music">Enable music</label>,
        <label for="musicvol">with volume</input>
        <input type="text" size="4" name="musicvol" id="musicvol"
          value="%(musicvol)s"> %%<br>
        <input type="checkbox" name="sound" id="sound" %(sound)s>
        <label for="sound">Enable sound</label>,
        <label for="soundvol">with volume</input>
        <input type="text" size="4" name="soundvol" id="soundvol"
          value="%(soundvol)s"> %%<br>
      </div>
      <div class="settings_tab" id="serversTab">
        <h1>Servers</h1>
        %(serverList)s

        <input type="checkbox" name="otherGames" %(otherGames)s>
        <label for="otherGames">If known servers have no compatible games,
          try unranked games hosted by others</label><br>
        <label for="lanGames">Search for unranked LAN games:</label>
        <select name="lanGames" id="lanGames">
          <option value="never" %(noLan)s>never</option>
          <option value="afterInet" %(lanAfterInet)s>if no games are
            found on known servers</option>
          <option value="beforeInet" %(lanBeforeInet)s>before looking for
            games on known servers</option>
        </select><br>
        <input type="checkbox" name="createGames" id="createGames"
          %(createGames)s> <label for="createGames">If known servers have no
          compatible games, start one (on a known server)</label><br>
      </div>
      <br>
      <input type="hidden" name="page" value="" id="pageinput">
      <input type="submit" value="Save">
    </form>
  </div>
<script type="text/javascript">
  %(setHash)s
  checkHash();
  setInterval(checkHash, 50);
  %(savedMsg)s
</script>
''' % {
    'resolutions': '\n'.join(resolutions),
    'windowed': '' if state.displaySettings.fullScreen else 'checked="1"',
    'fullscreen': 'checked="1"' if state.displaySettings.fullScreen else '',
    'xres': state.displaySettings.size[0],
    'yres': state.displaySettings.size[1],
    'alpha': 'checked="1"' if state.displaySettings.useAlpha else '',
    'clearwindows': 'checked="1"' if state.displaySettings.windowsTranslucent
        else '',
    'smoothpan': 'checked="1"' if state.displaySettings.smoothPanning else '',
    'playercentre': 'checked="1"' if state.displaySettings.centreOnPlayer
        else '',
    'music': 'checked="1"' if state.soundSettings.musicEnabled else '',
    'musicvol': state.soundSettings.musicVolume,
    'sound': 'checked="1"' if state.soundSettings.soundEnabled else '',
    'soundvol': state.soundSettings.soundVolume,
    'setHash': setHash,
    'savedMsg': savedMsg,
    'serverList': serverList,
    'otherGames': 'checked="1"' if state.connectionSettings.otherGames else '',
    'noLan': 'selected="1"' if state.connectionSettings.lanGames == 'none'
        else '',
    'lanBeforeInet': 'selected="1"' if state.connectionSettings.lanGames ==
        'beforeInet' else '',
    'lanAfterInet': 'selected="1"' if state.connectionSettings.lanGames ==
        'afterInet' else '',
    'createGames': 'checked="1"' if state.connectionSettings.createGames
        else '',
})

@core.addPage('/archives')
def archives(state, request):
    cmd = ['trosnoth', '--archives']
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    request.setResponseCode(302)
    request.setHeader('Location', '/')
    return message('Archives screen launched.')

def message(msg, title='Trosnoth'):
    return pageTemplate.apply(title=cgi.escape(str(title)),
            contents='<div class="central_message">%(message)s</div>' %
            {'message': cgi.escape(str(msg))})

@core.addPage('/settings/controls')
def controls(state, request):
    launchControls(state)
    request.setResponseCode(302)
    request.setHeader('Location', '/settings')
    return message('Controls customiser launched.')

@core.addPage('/ajax/keysettings')
def launchControls(state, request=None):
    if request:
        request.setHeader('Content-Type', 'text/plain')

    cmd = ['trosnoth', '--key-settings']
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return 'ok'

@core.addPage('/practise')
def practise(state, request):
    launchPractice(state)
    request.setResponseCode(302)
    request.setHeader('Location', '/')
    return message('Practise game launched.')

@core.addPage('/ajax/practise')
def launchPractice(state, request=None):
    if request:
        request.setHeader('Content-Type', 'text/plain')

    cmd = ['trosnoth', '--halfwidth=3', '--height=1', '--aicount=5']
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return 'ok'

@core.addPage('/ajax/play')
def launchPlayMenu(state, request=None):
    if request:
        request.setHeader('Content-Type', 'text/plain')

    cmd = ['trosnoth', '--play-menu']
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return 'ok'

@core.addPage('/credits')
def credits(state, request):
    if not hasattr(credits, '_cachedCredits'):
        creditsHTML = open(data.getPath(trosnoth.data.startupMenu,
                'credits.txt'), 'rU').read().strip()
        credits._cachedCredits = pageTemplate.apply(
            title='Trosnoth :: Credits',
            contents='''
  <marquee id="credits" behavior="scroll" direction="up" loop="-1" truespeed
  height="540px">
%(credits)s
  </marquee>
  <noscript><div class="notice">This would look better with
    JavaScript enabled.</div></noscript>
  <script type="text/javascript">
    var credits;
    function replaceMarqueeWithDiv() {
      var container = document.getElementById("container");
      var marquee = document.getElementById("credits");
      credits = document.createElement("div");
      var divCode ='<div style="height:548px;"></div>' + marquee.innerHTML;
      divCode += '<div style="height:548px;"></div>';
      credits.innerHTML = divCode;
      container.removeChild(marquee);
      credits.setAttribute("id", "credits");
      container.appendChild(credits);
    }
    function startCredits() {
      replaceMarqueeWithDiv();
      setInterval("scrollCredits()", 20);
    }
    function scrollCredits() {
      credits.scrollTop = credits.scrollTop + 3;
      if (credits.scrollTop >= credits.scrollHeight - credits.offsetHeight) {
        credits.scrollTop = 0;
      }
    }
    startCredits();
  </script>''' % {
    'credits': creditsHTML,
})
    return credits._cachedCredits

@core.addPage('/version', allOrigins=True)
def version(state, request):
    request.setHeader('Content-Type', 'text/plain')
    return '\n'.join([fullVersion] + list(validServerVersions))

@core.addPage('/shutdown')
def shutdown(state, request):
    log.warning('Shutting down Trosnoth core.')
    reactor.callLater(0.1, reactor.stop)
    return '''%(docType)s
<html>
<head>
<title>Trosnoth :: Shut down</title>
</head>
<body>
The Trosnoth core has shut down.
</body>
</html>''' % {
    'docType': DOCTYPE,
}

class CoreDisplay(Application):
    def __init__(self, state):
        Application.__init__(self,
            size=(300, 100),
            graphicsOptions=0,
            caption='Trosnoth Core',
            element=CoreDisplayInterface,
        )
        self.state = state

    def getFontFilename(self, fontName):
        '''
        Tells the UI framework where to find the given font.
        '''
        path = data.getPath(data, 'fonts', fontName)
        if os.path.isfile(path):
            return path
        raise IOError('font not found: %s' % (fontName,))

class CoreDisplayInterface(framework.CompoundElement):
    def __init__(self, app):
        framework.CompoundElement.__init__(self, app)
        self.coreLocation = Location((0, 0), 'topleft')

        font = Font('FreeSans.ttf', 12)
        self.elements = [
            PictureElement(app,
                image=NewImage(data.getPath(data, 'startupMenu', 'core.png')),
                pos=self.coreLocation,
            ),
            TextElement(app,
                text='Trosnoth core is running.',
                font=font,
                pos=Location((200, 0), 'midtop'),
                colour=(192, 192, 255),
                backColour=(0, 0, 0),
                anchor='midtop',
            ),
            TextButton(app,
                pos=Location((200, 50), 'midtop'),
                text='View menu (in browser)',
                font=font,
                stdColour=(192, 192, 255),
                hvrColour=(255, 255, 255),
                backColour=(0, 0, 0),
                onClick=self.viewMenuClicked,
            ),
            TextButton(app,
                pos=Location((200, 75), 'midtop'),
                text='Shut down core',
                font=font,
                stdColour=(192, 192, 255),
                hvrColour=(255, 255, 255),
                backColour=(0, 0, 0),
                onClick=self.shutDownClicked,
            ),
        ]

    def viewMenuClicked(self, btn):
        self.app.state.openBrowser()

    def shutDownClicked(self, btn):
        reactor.stop()

    def tick(self, deltaT):
        y = self.coreLocation.point[1]
        y -= deltaT * 80
        if y < -100:
            y += 100
        self.coreLocation.point = (0, y)

class CoreState(ServerState):
    def __init__(self, options):
        ServerState.__init__(self, core)
        pygame.display.init()
        self.options = options
        self.connectionSettings = ConnectionSettings(None)
        self.displaySettings = DisplaySettings(None)
        self.soundSettings = SoundSettings(None)

    def _createSite(self):
        resources = Resources(self)
        return LocallyListeningSite(resources)

    def begin(self):
        try:
            reactor.listenTCP(8099, self.site)
        except CannotListenError:
            log.error('Could not listen on port 8099.')
            log.error('Is the Trosnoth core already running?')
            sys.exit(1)

        if self.options.browser:
            reactor.callLater(0, self.openBrowser)

        if self.options.showCore:
            coreDisplay = CoreDisplay(self)
            coreDisplay.run_twisted()
        else:
            if self.options.browser:
                log.warning('Trosnoth core started.')
            else:
                log.warning('Trosnoth core started. Go to '
                        'http://localhost:8099/ for menu.')
            reactor.run()

    def openBrowser(self):
        webbrowser.open_new('http://localhost:8099/')

    def isServerKnown(self, host, port):
        return any((host, port) == (h, p) for (h, p, w) in
                self.connectionSettings.servers)

    def playGame(self, host, port):
        cmd = ['trosnoth', '--auth-server=%s:%d' % (host, port)]
        subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def addServer(self, host, port, website):
        self.connectionSettings.servers.append((host, port, website))
        self.connectionSettings.save()

class LocallyListeningSite(server.Site):
    def buildProtocol(self, addr):
        if addr.host == "127.0.0.1":
            return server.Site.buildProtocol(self, addr)
        return None

parser = OptionParser()
parser.add_option('-H', '--hide-core', action='store_false', dest='showCore',
    default=True, help='do not show the core visibly. Using this option also '
    'means that no browser window will be opened unless it is explicitly '
    'requested with --open-browser.')
parser.add_option('-b', '--open-browser', action='store_true', dest='browser',
    default=False, help='open a browser window showing the menu')
parser.add_option('-n', '--no-browser', action='store_true', dest='noBrowser',
    help='do not open a browser window showing the menu')
parser.add_option('-d', '--debug', action='store_true', dest='debug',
    help='show debug-level messages on console')
parser.add_option('-l', '--log-file', action='store', dest='logFile',
    help='file to write logs to')

def commandLine():
    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error('no arguments expected')
    if options.browser:
        if options.noBrowser:
            parser.error('--open-browser and --no-browser are incompatible')
    elif not options.noBrowser:
        if options.showCore:
            options.browser = True
        else:
            options.browser = False
    return options

def main():
    options = commandLine()
    initLogging(options.debug, options.logFile)

    state = CoreState(options)
    state.begin()

if __name__ == '__main__':
    main()
