from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext, Context
from django.core import serializers

from postit.models import PostIt, UserProfile
from postit.forms import PostItForm

def postit(request):
	postits = PostIt.objects.all()
	return render_to_response('postits.html', { 'postits': postits }, mimetype='text/html', context_instance=RequestContext(request))

def postit_edit_or_new(request, id=None):
	if id:
		postit = get_object_or_404(PostIt, pk=id)
	else:
		postit = PostIt()
	form = PostItForm(request.POST or None, instance=postit)
	if form.is_valid():
		form.save()
		return redirect('postit')
	return render_to_response('form.html', { 'form': form }, mimetype='text/html', context_instance=RequestContext(request))

def postit_delete(request, id):
	get_object_or_404(PostIt, pk=id).delete()
	return redirect('postit')

def postit_by_filter(request, filter=None, selector=None):
	if filter == 'user':
		postits = PostIt.objects.filter(user_to=selector) 
		selector = User.objects.filter(id=selector)[0]
	if filter == 'status':
		postits = PostIt.objects.filter(status=selector)
	return render_to_response('postits_filtered.html', { 'postits': postits, 'status':selector }, mimetype='text/html', context_instance=RequestContext(request))

def postit_export(request):
    data = serializers.serialize("xml", PostIt.objects.all())
    return render_to_response('export.xml', { 'data': data }, mimetype='text/html', context_instance=RequestContext(request))

# def postit_action(request, action=None, id=None):
# 	print action
# 	if action == 'delete':
# 		get_object_or_404(PostIt, pk=id).delete()
# 		return redirect('postit')
# 	if action == 'edit' or action =='new':
# 		if id:
# 			postit = get_object_or_404(PostIt, pk=id)
# 		else:
# 			postit = PostIt()
# 		form = PostItForm(request.POST or None, instance=postit)
# 		if form.is_valid():
# 			form.save()
# 		return render_to_response('postits_filtered.html', { 'postit': postit, 'status':action }, mimetype='text/html', context_instance=RequestContext(request))

	