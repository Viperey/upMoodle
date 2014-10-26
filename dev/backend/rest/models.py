from django.db import models
from rest.exceptions import ExtensionError
from rest.finals import *


# Carrer, course, subject
class LevelType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    type = models.ForeignKey('LevelType')
    visible = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class User(models.Model):
    id = models.AutoField(primary_key=True)
    rol = models.ForeignKey('Rol')
    email = models.EmailField(max_length=100)
    nick = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    profilePic = models.ImageField(upload_to='pics/users', blank=True)
    lastTimeActive = models.DateField(auto_now=True)
    joined = models.DateField(auto_now_add=True)
    banned = models.BooleanField(default=False)
    sessionToken = models.CharField(max_length=1000, blank=True)

    def __unicode__(self):
        return self.nick


class NoteBoard(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=100)
    text = models.CharField(max_length=2000)
    level = models.ForeignKey('Level')

    def __unicode__(self):
        return self.topic


# SHA1. 64 alphabetical chars
class BannedHash(models.Model):
    hash = models.CharField(primary_key=True, max_length=65)

    def __unicode__(self):
        return self.hash


class CalendarFrequency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class CalendarRegularEvent(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    text = models.CharField(max_length=2000)
    created = models.DateField(auto_now_add=True)
    lastUpdate = models.DateField(auto_now=True)
    author = models.ForeignKey(User, null=False, related_name='regular_lastUpdated')
    lastUpdated = models.ForeignKey(User, null=False, related_name='regular_author')
    level = models.ForeignKey('Level')

    def __unicode__(self):
        return self.title


class CalendarEventDate(models.Model):
    id = models.AutoField(primary_key=True)
    idEvent = models.ForeignKey(CalendarRegularEvent, related_name='dates')
    index = models.IntegerField(default=1)
    hourStart = models.TimeField(null=True)
    hourEnd = models.TimeField(null=True)
    allDay = models.BooleanField(default=False)
    frequency = models.ForeignKey('CalendarFrequency', default=DEFAULT_FREQUENCY)

    def __unicode__(self):
        return '[%s to %s] %s' % (self.hourStart, self.hourEnd, self.frequency)


class Year(models.Model):
    id = models.AutoField(primary_key=True)
    verbose = models.CharField(max_length=20)

    def __unicode__(self):
        return self.verbose


class File(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Level)
    hash = models.CharField(max_length=65)
    name = models.CharField(max_length=100)
    year = models.ForeignKey(Year)
    fileType = models.CharField(max_length=50)
    uploaded = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(User, related_name='file_lastUpdater')
    lastUpdate = models.DateTimeField(auto_now=True)
    lastUpdater = models.ForeignKey(User, related_name='file_updater')
    visible = models.BooleanField(default=True)
    file = models.FileField(upload_to='files')

    def __unicode__(self):
        return self.name

    def extension(self):
        index = self.file.name.rfind('.')
        if index == -1 or ((len(self.file.name) - index - 1) > 4):
            raise ExtensionError
        return self.file.name[index+1:]


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class FileTag(models.Model):
    idFile = models.ForeignKey(File)
    idTag = models.ForeignKey(Tag)

    def __unicode__(self):
        return '%s - %s' % (self.idFile, self.idTag)


class FileReportList(models.Model):
    idFile = models.ForeignKey(File)
    idReporter = models.ForeignKey(User)
    comment = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s @ %s' % (self.comment[0:10], self.idFile)


class FileComments(models.Model):
    id = models.AutoField(primary_key=True)
    idFile = models.ForeignKey(File)
    idAuthor = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=1000)

    def __unicode__(self):
        return '%s @ %s' % (self.text[0:10], self.idFile)
