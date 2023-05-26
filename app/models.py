from django.db import models

class Tag(models.Model):
    aspect = models.CharField(max_length=100)
    sentiment = models.CharField(max_length=3, choices=(
        ('POS', 'Positive'),
        ('NEG', 'Negative'),
        ('NEU', 'Neutral'),
    ))

    def __str__(self) -> str:
        return f"aspect: {self.aspect} - sentiment: {self.sentiment}"


class SheetModel(models.Model):
   name = models.CharField(max_length=255)
   row_count = models.PositiveBigIntegerField()

   def __str__(self) -> str:
        return f"{self.name} sheets has {self.row_count} rows"

class TrainingData(models.Model):
    text = models.TextField(null=True)
    tags = models.ManyToManyField(Tag)
    sheet = models.ForeignKey(SheetModel, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.text

