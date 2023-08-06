from django import forms
from django.contrib.auth.models import User

from tinymce.widgets import TinyMCE
from captcha.fields import CaptchaField

from models import Post, Comment

class PostFormAdmin(forms.ModelForm):
    """
    Form for creating and editing posts in the admin section
    """
    content = forms.CharField(required=False, widget=TinyMCE())

    class Meta:
        model = Post

class BlogModelFormBase(forms.ModelForm):
    """
    Define some defaults
    """
    error_css_class = 'error'
    required_css_class = 'required'
    
class CommentForm(BlogModelFormBase):
    """
    Form for the creation of a new comment
    """
    author = forms.CharField(required=False)
    email = forms.EmailField()
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'cols': '60', 'rows': '10' })
        )
    verification = CaptchaField(
        help_text='Please type the letters in the image')

    class Meta:
        model = Comment
        exclude = ('post',)
