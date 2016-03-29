from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Pool(models.Model):
    tournament = models.ForeignKey('matches.Tournament')
    players = models.ManyToManyField('players.Player')

    def __str__(self):
        return '{} - Pool {}'.format(self.tournament.name, self.id)

    def _generate_matches(self):
        """
        Create a match for each set of 2 players in the pool, and rounds to hold
        them
        """
        from matches.models import Match, Round

        rounds = []
        matches = []
        players = [player for player in self.players.all()]

        if len(players) % 2 != 0: players.append(None)

        iterator = list(range(len(players)))
        for x in iterator:
            if x == 0: continue
            round = Round(pool=self, number=x)
            round.save()
            rounds.append(round)

        for x in iterator:
            if not players[x]: continue

            others_iterator = iterator.copy()
            others_iterator.remove(x)

            for y in others_iterator:
                if not players[y]: continue
                
                match_exists = Match.objects.filter(player_1_init=players[x], player_2_init=players[y]).exists()
                inverse_match_exists = Match.objects.filter(player_1_init=players[y], player_2_init=players[x]).exists()

                if match_exists or inverse_match_exists:
                    continue

                match = Match(
                    player_1_init=players[x],
                    player_2_init=players[y],
                    round=rounds[len(matches) % len(rounds)],
                    round_index=0
                )
                match.save()
                matches.append(match)
