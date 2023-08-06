# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.list_detail import object_detail

from faq.models import Topic, Question
from faq.views.shallow import _fragmentify


def topic_detail(request, slug):
    """
    A detail view of a Topic

    Templates:
        :template:`faq/topic_detail.html`
    Context:
        topic
            An :model:`faq.Topic` object.
        question_list
            A list of all published :model:`faq.Question` objects that relate
            to the given :model:`faq.Topic`.

    """
    extra_context = {
        'question_list': Question.objects.published().filter(topic__slug=slug),
    }

    return object_detail(request, queryset=Topic.objects.published(),
        extra_context=extra_context, template_object_name='topic', slug=slug)


def question_detail(request, topic_slug, slug):
    """
    A detail view of a Question.

    Simply redirects to a detail page for the related :model:`faq.Topic`
    (:view:`faq.views.topic_detail`) with the addition of a fragment
    identifier that links to the given :model:`faq.Question`.
    E.g. ``/faq/topic-slug/#question-slug``.

    """
    url = reverse('faq-topic-detail', kwargs={'slug': topic_slug})
    return _fragmentify(Question, slug, url)
