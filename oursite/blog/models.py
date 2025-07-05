from django.db import models
from django import forms

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet

from datetime import date

from modelcluster.models import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class BlogIndexPage(Page):

    description = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description")
    ]



class BlogPostTag(TaggedItemBase):

    content_object = ParentalKey("BlogPostPage", related_name="tagged_items",
                                 on_delete=models.CASCADE)



class BlogPostPage(Page):

    date = models.DateField("Post Date", default=date.today)
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField("blog.Author", blank=True)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)


    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("authors", widget=forms.CheckboxSelectMultiple),
        FieldPanel("intro"),
        FieldPanel("body"),
        InlinePanel("image_gallery", label="gallery images"),
        FieldPanel("tags")
    ]


class BlogPageImageGallery(Orderable):

    page = ParentalKey(BlogPostPage, related_name="image_gallery",
                       on_delete=models.CASCADE)
    image = models.ForeignKey("wagtailimages.Image", related_name="+",
                              on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, blank=True)

    panels = [FieldPanel("image"), FieldPanel("caption")]


@register_snippet
class Author(models.Model):

    name = models.CharField(max_length=255)
    author_image = models.ForeignKey("wagtailimages.Image", related_name="+",
                              on_delete=models.CASCADE)
    
    panels = [
        FieldPanel("name"), 
        FieldPanel("author_image")
    ]

    def __str__(self):
        return self.name
    

class TagIndexPage(Page):
    def get_context(self, request):
        tag = request.GET.get("tag")

        if tag:
            blogposts = BlogPostPage.objects.live().filter(tags__name=tag)
        else:
            blogposts = BlogPostPage.objects.none()

        context = super().get_context(request)
        context["blogposts"] = blogposts
        context["tag"] = tag

        return context