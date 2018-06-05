from django.conf import settings
from graphene_django import DjangoObjectType
import graphene
from .models import Note as NoteModel
from django.contrib.auth.models import User as UserModel


class Note(DjangoObjectType):
    class Meta:
        model = NoteModel

        # Describe the data as a ndoe in the graph for GraphQL
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    note = graphene.List(Note, id=graphene.String(), title=graphene.String())
    all_notes = graphene.List(Note)

    def resolve_all_notes(self, info):
        # Decide which notes to return.

        user = info.context.user

        # if settings.DEBUG:
        #     return NoteModel.objects.all()
        # elif user.is_anonymous:
        if user.is_anonymous:
            return NoteModel.objects.none()
        else:
            return NoteModel.objects.filter(user=user)

    def resolve_note(self, info, **kwargs):
        # .get returns None if the title does note exist
        title = kwargs.get('title')
        # id = kwargs.get('id')

        if title is not None:
            return Note.objects.get(title=title)

        return None


class CreateNote(graphene.Mutation):

    class Arguments:
        # input attribs for the mutation
        title = graphene.String()
        content = graphene.String()

    # output fields after mutation
    ok = graphene.Boolean()
    note = graphene.Field(Note)

    def mutate(self, info, title, content):
        user = info.context.user

        if user.is_anonymous:
            is_ok = False
            return CreateNote(ok=is_ok)

        else:
            new_note = NoteModel(title=title, content=content, user=user)
            is_ok = True
            new_note.save()

            return CreateNote(note=new_note, ok=is_ok)

class User(DjangoObjectType):
    class Meta:
        model = UserModel

        # Describe the data as a ndoe in the graph for GraphQL
        interfaces = (graphene.relay.Node, )

class RegisterUser(graphene.Mutation):

    class Arguments:
        username = graphene.String()
        password = graphene.String()

    user = graphene.Field(User)

    def mutate(self, info, username, password):
        new_user = UserModel(username=username, password=password)
        new_user.save()

        return RegisterUser(user=new_user)

class Mutation(graphene.ObjectType):
    create_note = CreateNote.Field()
    register_user = RegisterUser.Field()


            # Add a schema and attach the query
schema = graphene.Schema(query=Query, mutation=Mutation)
