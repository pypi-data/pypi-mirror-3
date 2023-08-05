from django.conf.urls.defaults import *
import re
import consent.regexps

urlpatterns = patterns('consent.django.apps.kui.views',

    #
    ##  Application Home Page

    (r'^$',
        'kui.welcome'),

    #
    ##  About 

    (r'^about/$',
        'kui.about'),

    #
    ##  Feed 

    (r'^feed/$',
        'kui.feed'),

    #
    ##  Account recovery

    (r'^recover/$',
        'accesscontrol.recover'),
    #
    ##  User Authentication

    (r'^login/(?P<returnPath>(.*))$',
        'accesscontrol.login'),
    (r'^logout/$',
        'accesscontrol.logout'),

    #
    ##  Administration
    
    (r'^admin/model/create/(?P<className>(\w*))/$',
        'admin.create'),

    (r'^admin/model/update/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.update'),

    (r'^admin/model/delete/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.delete'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.listHasMany'),

    (r'^admin/model/create/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.createHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.readHasMany'),

    (r'^admin/model/update/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.updateHasMany'),

    (r'^admin/model/delete/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.deleteHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/$',
        'admin.read'),

    (r'^admin/model/(?P<className>([^/]*))/$',
        'admin.list'),

    (r'^admin/model/$',
        'admin.model'),

    (r'^admin/$',
        'admin.index'),

    #
    ##  Access Control
    
    (r'^accessDenied/(?P<deniedPath>(.*))$',
        'kui.accessDenied'),

    #
    ##  Person

    (r'^people/create/(?P<returnPath>(.*))$',
        'person.create'),
        
    (r'^people/$',
        'person.list'),
        
    (r'^people/find/(?P<startsWith>[\w\d]+)/$',
        'person.search'),
        
    (r'^people/find/$',
        'person.search'),
        
    (r'^people/search/$',
        'person.search'),
        
    (r'^people/home/$',
        'person.read'),
        
    (r'^people/(?P<personName>%s)/$' % consent.regexps.personName,
        'person.read'),
        
    (r'^people/(?P<personName>%s)/home/$' % consent.regexps.personName,
        'person.read'),
        
    (r'^people/(?P<personName>%s)/edit/$' % consent.regexps.personName,
        'person.update'),
        
    (r'^people/(?P<personName>%s)/delete/$' % consent.regexps.personName,
        'person.delete'),

    #
    ##  Assembly

    (r'^assemblies/create/(?P<returnPath>(.*))$', 'assembly.create'),
    (r'^assemblies/$', 'assembly.list'),
    (r'^assemblies/find/(?P<startsWith>[\w\d]+)/$', 'assembly.search'),
    (r'^assemblies/find/$', 'assembly.search'),
    (r'^assemblies/search/$', 'assembly.search'),
    (r'^assemblies/(?P<assemblyId>(\d+))/$', 'assembly.read'),
    (r'^assemblies/(?P<assemblyId>(\d+))/home/$', 'assembly.read'),
    (r'^assemblies/(?P<assemblyId>(\d+))/edit/$', 'assembly.update'),
    (r'^assemblies/(?P<assemblyId>(\d+))/delete/$', 'assembly.delete'),

    #
    ##  Proposal

    (r'^proposals/create/(?P<returnPath>(.*))$', 'proposal.create'),
    (r'^proposals/$', 'proposal.list'),
    (r'^proposals/find/(?P<startsWith>[\w\d]+)/$', 'proposal.search'),
    (r'^proposals/find/$', 'proposal.search'),
    (r'^proposals/search/$', 'proposal.search'),
    (r'^proposals/(?P<proposalId>(\d+))/$', 'proposal.read'),
    (r'^proposals/(?P<proposalId>(\d+))/home/$', 'proposal.read'),
    (r'^proposals/(?P<proposalId>(\d+))/edit/$', 'proposal.update'),
    (r'^proposals/(?P<proposalId>(\d+))/delete/$', 'proposal.delete'),

    #
    ## SSH Key 
    
    (r'^people/(?P<personName>%s)/sshKeys/$' % consent.regexps.personName,
        'sshKey.list'),

    (r'^people/(?P<personName>%s)/sshKeys/create/$' % consent.regexps.personName,
        'sshKey.create'),

    (r'^people/(?P<personName>%s)/sshKeys/(?P<sshKeyId>(\d*))/delete/$' % (
        consent.regexps.personName),  
        'sshKey.delete'),

    (r'^people/(?P<personName>%s)/sshKeys/(?P<sshKeyId>(\d*))/$' % (
        consent.regexps.personName),  
        'sshKey.read'),

    #
    ## API Key
    (r'^people/(?P<personName>%s)/apikey/$' % consent.regexps.personName,
        'person.apikey'),
            

    #
    ##  Project

    (r'^projects/create/(?P<returnPath>(.*))$',
        'project.create'),
        
    (r'^projects/$',
        'project.list'),
        
    (r'^projects/find/(?P<startsWith>[\w\d]+)/$',
        'project.search'),
        
    (r'^projects/find/$',
        'project.search'),
        
    (r'^projects/search/$',
        'project.search'),
        
    (r'^projects/home/$',
        'project.read'),
        
    (r'^projects/(?P<projectName>%s)/$' % consent.regexps.projectName,
        'project.read'),
        
    (r'^projects/(?P<projectName>%s)/home/$' % consent.regexps.projectName,
        'project.read'),
        
    (r'^projects/(?P<projectName>%s)/edit/$' % consent.regexps.projectName,
        'project.update'),
        
    (r'^projects/(?P<projectName>%s)/delete/$' % consent.regexps.projectName,
        'project.delete'),

    (r'^projects/(?P<projectName>%s)/join/$' % consent.regexps.projectName,
        'project.join'),
        

    #
    ##  Member

    (r'^projects/(?P<projectName>%s)/members/$' % consent.regexps.projectName,
        'member.list'),
        
    (r'^projects/(?P<projectName>%s)/members/create/$' % consent.regexps.projectName,
        'member.create'),
        
    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/edit/$' % (
        consent.regexps.projectName, consent.regexps.personName),  
        'member.update'),
        
    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/delete/$' % (
        consent.regexps.projectName, consent.regexps.personName),  
        'member.delete'),

    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/approve/$' % (
        consent.regexps.projectName, consent.regexps.personName),  
        'member.approve'),

    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/reject/$' % (
        consent.regexps.projectName, consent.regexps.personName),  
        'member.reject'),

    #
    ##  Service
    
    (r'^projects/(?P<projectName>%s)/services/$' % consent.regexps.projectName,
        'service.list'),

    (r'^projects/(?P<projectName>%s)/services/create/$' % consent.regexps.projectName,
        'service.create'),

    (r'^projects/(?P<projectName>%s)/services/(?P<serviceName>%s)/edit/$' % (
        consent.regexps.projectName, consent.regexps.serviceName),  
        'service.update'),

    (r'^projects/(?P<projectName>%s)/services/(?P<serviceName>%s)/delete/$' % (
        consent.regexps.projectName, consent.regexps.serviceName),  
        'service.delete'),

    (r'^projects/(?P<projectName>%s)/services/(?P<serviceName>%s)/$' % (
        consent.regexps.projectName, consent.regexps.serviceName),  
        'service.read'),

    #
    ##  API

    (r'^api.*$',
        'api.api'),


    #
    ##  Not Found

    (r'^.*/$',
        'kui.pageNotFound'),
)

