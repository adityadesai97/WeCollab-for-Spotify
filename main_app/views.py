# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from urllib import urlencode
import datetime
import math
import random
import requests
import base64
import json

client_id = '13d307bdb31e41a7a6a36be9376f7954';
client_secret = 'a3b9dcff157c4a7c98e0b593bc0da7a8';
redirect_uri = 'http://localhost:8000/callback';

stateKey = 'spotify_auth_state'
scope = 'user-read-private user-read-email playlist-read-collaborative playlist-modify-private playlist-modify-public'

playlist_names = []
playlists = []
access_token = ''
refresh_token = ''

def generateRandomString(length):
	text = ''
	possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
	for i in range(0, length):
		text = text + str(possible[int(math.floor(random.random() * len(possible)))])
	return text

def home(request):
	return render(request, 'index.html')

def login(request):
	if request.method == 'GET':
		state = generateRandomString(16);
		querydict = {
			'response_type': 'code', 
			'client_id': client_id, 
			'scope': scope, 
			'redirect_uri': redirect_uri, 
			'state': state
		}
		response = redirect('https://accounts.spotify.com/authorize?' + urlencode(querydict))
		response.set_cookie(stateKey, state)

		return response

def callback(request):
	if request.method == 'GET':
		code = request.GET.get('code')
		state = request.GET.get('state') 
		storedState = request.COOKIES[stateKey]
		response = HttpResponse('hi')

		if state == None or state != storedState:
			querydict = {
				'error': 'state_mismatch'
				}
			response = redirect('/home#' + urlencode(querydict))
		else:
			authOptions = {
				'code': code, 
				'redirect_uri': redirect_uri, 
				'grant_type': 'authorization_code'
			}
			r = requests.request(method = 'POST', url = 'https://accounts.spotify.com/api/token', data = authOptions, headers = {'Authorization': 'Basic ' + base64.b64encode(client_id + ':' + client_secret)})
			if r.status_code == 200:
				resp = json.loads(r.content.replace("'", "\""))['access_token']
				request.session['access_token'] = json.loads(r.content.replace("'", "\""))['access_token']
				request.session['refresh_token'] = json.loads(r.content.replace("'", "\""))['access_token']
				access_token = json.loads(r.content.replace("'", "\""))['access_token']
				refresh_token = json.loads(r.content.replace("'", "\""))['access_token']

				r = requests.request(method = 'GET', url = 'https://api.spotify.com/v1/me/', headers = {'Authorization': 'Bearer ' + access_token})
				current_user = json.loads(r.content.replace("'", "\""))['id']

				playlist_names = []
				playlists = []

				r = requests.request(method = 'GET', url = 'https://api.spotify.com/v1/me/playlists', headers = {'Authorization': 'Bearer ' + access_token})
				for item in json.loads(r.content.replace("'", "\""))['items']:
					if item['collaborative'] == True and item['owner']['id'] == current_user:
						playlist_names.append(item['name'])
						playlists.append(item)

				request.session['playlist_names'] = playlist_names
				request.session['playlists'] = playlists

				querydict = {
					'step': '2',
					'names': ','.join(playlist_names)
				}
				response = redirect('/home#' + urlencode(querydict))

			else:
				querydict = {
					'error': 'state_mismatch'
				}
				response = redirect('/home#' + urlencode(querydict))

	return response

@csrf_exempt
def next(request):
	if request.method == 'POST':
		allowed_users = request.POST['members']
		for item in request.session.get('playlists'):
			if item['name'] == request.POST['name']:
				chosen_track = item
				break
		to_delete = []
		r = requests.request('GET', chosen_track['tracks']['href'], headers = {'Authorization': 'Bearer ' + request.session.get('access_token')})
		for item in json.loads(r.content.replace("'", "\""))['items']:
			if item['added_by']['id'] not in allowed_users:
				to_delete.append({'uri': item['track']['uri']})

		r = requests.request(method = 'DELETE', url = chosen_track['tracks']['href'], json = {'tracks': to_delete}, headers = {'Authorization': 'Bearer ' + request.session.get('access_token'), 'Content-Type': 'json'})

		# querydict = {
		# 	'step': '3'
		# }
		# response = redirect('/home#' + urlencode(querydict))
		# print(response)

	return HttpResponse('hii')
