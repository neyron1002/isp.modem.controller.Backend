from django.db import models
import uuid

class Modem(models.Model):
    IdModem = models.AutoField(primary_key=True)
    Manufacturer = models.CharField(max_length=100)
    Oui = models.CharField(max_length=100)
    ProductClass = models.CharField(max_length=100)
    JsonParameters = models.TextField()

    class Meta:
        db_table = 'Modem'
        managed = False

    def __str__(self):
        return f"{self.Manufacturer} - {self.Oui} - {self.ProductClass}"

class ACServer(models.Model):
    IdACServer = models.AutoField(primary_key=True)
    IdCompany = models.UUIDField(default=uuid.uuid4, unique=True)
    ServerAccessIp = models.CharField(max_length=100)
    Port = models.CharField(max_length=100)
    JsonParameters = models.TextField()
    IsEnabled = models.BooleanField()
    DatetimeCreated = models.DateField()

    class Meta:
        db_table = 'ACServer'
        managed = False

    def __str__(self):
        return f"Server {self.IdACServer} - {self.ServerAccessIp}:{self.Port}"

class TermGroup(models.Model):
    IdTermGroup = models.AutoField(primary_key=True)
    NameGroup = models.CharField(max_length=100)

    class Meta:
        db_table = 'TermGroup'
        managed = False

    def __str__(self):
        return self.NameGroup

class Term(models.Model):
    IdTerm = models.AutoField(primary_key=True)
    IdTermGroup = models.ForeignKey(TermGroup, on_delete=models.CASCADE)
    Term = models.CharField(max_length=100)
    Enable = models.BooleanField()
    Icon = models.CharField(max_length=100)

    class Meta:
        db_table = 'Term'
        managed = False

    def __str__(self):
        return self.Term
