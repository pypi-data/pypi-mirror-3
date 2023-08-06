from queryset_client.client import Client


from .utils import get_client
client = get_client()



def test_len1():
    message = client.message.objects.all()
    assert len(message) == client.message.objects.count()


def test_len2():
    message = client.message.objects.all()
    assert len(message) == client.message.objects.all().count()