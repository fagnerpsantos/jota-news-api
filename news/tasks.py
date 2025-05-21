from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from news.models import News
from users.models import User


@shared_task(bind=True, max_retries=3)
def send_news_published_notification(self, news_id):
    """
    Tarefa para enviar notificação por e-mail (texto puro)
    """
    try:
        news = News.objects.get(id=news_id)
        subscribers = User.objects.filter(
            is_active=True,
            role='READER',
            subscription__is_active=True
        ).distinct()

        subject = f"🚀 Nova Notícia Publicada: {news.title}"
        message = f"""
        Olá,

        Uma nova notícia foi publicada no JOTA News:

        Título: {news.title}
        Subtítulo: {news.subtitle or 'Sem subtítulo'}

        Resumo:
        {news.content[:150]}...

        Acesse a notícia completa em: jota_api/news/{news.id}

        Atenciosamente,
        Equipe JOTA News
        """

        recipient_list = [user.email for user in subscribers]

        send_mail(
            subject,
            message.strip(),  # Remove espaços em branco extras
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False
        )

        return f"E-mails enviados para {len(recipient_list)} assinantes"

    except Exception as e:
        self.retry(exc=e, countdown=60)


@shared_task
def publish_scheduled_news():
    """
    Tarefa periódica para publicar notícias agendadas
    """
    from django.utils import timezone
    scheduled_news = News.objects.filter(
        status='PUBLISHED',
        scheduled_date__lte=timezone.now(),
        is_published=False
    )

    for news in scheduled_news:
        news.publication_date = timezone.now()
        news.is_published = True
        news.save()
        send_news_published_notification.delay(news.id)

    return f"{scheduled_news.count()} notícias agendadas publicadas"