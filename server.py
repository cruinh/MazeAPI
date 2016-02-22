#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
import json
from pprint import pprint
from flask import Flask, jsonify, redirect, request
from copy import deepcopy

app = Flask(__name__)
# global playerPosition
playerPosition = 0,0
win = False

traversableMapValues = ["0", "S", "E"]
nontraversableMapValues = ["1","S","E"]
winningValue = "E"

def playerMove(x,y):
	global playerPosition
	print "playerMove(" + str(x) + "," + str(y) + ") from playerPosition:("+str(playerPosition) + ")"
	playerX, playerY = playerPosition
	newX = playerX + x
	newY = playerY + y
	try:
		positionValue = mapData[newY][newX]
		if positionValue in traversableMapValues:
			playerPosition = newX, newY
			if positionValue == winningValue:
				print "winning move!" + "\n\tplayerPosition:" + str(playerPosition) + "\n\tmoveBy:" + str(x) + "," + str(y) + "\n\tnewPosition:" + str(newX) + "," + str(newY)
				global win
				win = True
				return jsonify({"result": "Found the exit!.  You made it through the maze!  send a GET to /restart to try again."})
			else:
				print "valid move." + "\n\tplayerPosition:" + str(playerPosition) + "\n\tmoveBy:" + str(x) + "," + str(y) + "\n\tnewPosition:" + str(newX) + "," + str(newY)
				return jsonify({"result": "success.  but are you closer to the exit?"})
		elif positionValue in nontraversableMapValues:
			print "INVALID move." + "\n\tplayerPosition:" + str(playerPosition) + "\n\tmoveBy:" + str(x) + "," + str(y) + "\n\ttargetPosition:\"" + str(newX) + "," + str(newY) + "\n\ttargetValue:\"" + str(positionValue) + "\""
			return jsonify({"result":"can't go that way"})
		else:
			print "cancelling move.  target map location with unrecognized value: \"" + str(positionValue) + "\"" 
			return jsonify({"unrecognized target map location value":positionValue})
	except Exception, e:
		print "error while moving: " + str(e) + "\n\tplayerPosition:" + str(playerPosition) + "\n\tmoveBy:" + str(x) + "," + str(y)
		return jsonify({"result":"can't go that way", "error":str(e)})

def parseMapJSON():
	with open('map.json') as data_file:
		global jsonData
		jsonData = json.load(data_file)
		global mapData
		mapData = jsonData["map"]

	global startPosition
	startPosition = -1,-1
	global endPosition
	endPosition = -1,-1

	r = 0
	try:
		while mapData[r] is not None:
			c = 0
			currentRow = mapData[r]
			try:
				while currentRow[c] is not None:
					currentPositionValue = currentRow[c]
					if currentPositionValue == "S":
						startPosition = c,r
					elif currentPositionValue == "E":
						endPosition = c,r
					c = c + 1
			except Exception, e:
				 r = r + 1
	except Exception, e:
		pass

	# pprint(startPosition)
	# pprint(endPosition)
	global playerPosition
	playerPosition = startPosition
	print "player position: " + str(playerPosition)

@app.route("/")
def intro():
	return jsonify({"message": "You're stuck in a maze. Send GET requests to any of the following endpoints to find your way through to the exit: /moveLeft, /moveRight, /moveDown, /moveUp.  If you get hopelessly lost, GET /restart to start over from the beginning."})

@app.route("/map")
def showMap():
	secret = request.args.get('secret')
	password = request.args.get('password')
	if secret == "iamspecial":
		global jsonData
		global mapData
		global playerPosition
		playerX, playerY = playerPosition
		mapCopy = deepcopy(mapData)
		mapCopy[playerY][playerX] = "P"
		mapJSON = {"map": mapCopy}
		return jsonify(mapJSON)
	elif secret is not None or password is not None:
		return jsonify({"result":"nice try.  that's not the secret."})
	else:
		return jsonify({"result":"what's the secret password?"})

@app.route("/restart")
def restart():
	global win
	win = False
	parseMapJSON()
	return redirect("/", code=302)

@app.route("/moveLeft")
def playerMoveLeft():
	return playerMove(-1,0)

@app.route("/moveRight")
def playerMoveRight():
	return playerMove(1,0)

@app.route("/moveUp")
def playerMoveUp():
	return playerMove(0,-1)

@app.route("/moveDown")
def playerMoveDown():
	return playerMove(0,1)

if __name__ == "__main__":
	parseMapJSON()
	app.run(port=8080)
	# app.run('localhost', debug=True, port=8080)