from django import template

from glip.clips.models import Game, GameFollow

register = template.Library()


@register.filter(name="check_relationship_exists")
def check_relationship_exists(game_object, user):
    # user_id = int(user.id)  # get the user id
    game = Game.objects.get(game_id=game_object["id"])
    if GameFollow.objects.filter(following=user, followed=game).exists():
        return True
    else:
        return False
    # return game_object.objects.filter(following=user_id).exists()  # check if relationship exists
