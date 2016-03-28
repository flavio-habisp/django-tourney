import json

from django.test import TestCase
from django.core.exceptions import ValidationError

from model_mommy import mommy

from matches.models import Bracket, Match, Tournament
from players.models import Player


class TournamentTestCase(TestCase):

    def test_basics(self):
        """
        Test the basic functionality of Tournament
        """
        tournament = mommy.make(Tournament, name='My Test Tournament')
        tournament.players.add(mommy.make(Player))
        tournament.players.add(mommy.make(Player))

        self.assertEqual(tournament.name, 'My Test Tournament')
        self.assertEqual(tournament.slug, 'my-test-tournament')
        self.assertEqual(tournament.players.count(), 2)
        

class BracketTestCase(TestCase):

    def setUp(self):
        self.bracket = mommy.make(Bracket, name='My Test Bracket')

    def test_basics(self):
        """
        Test the basic functionality of the Bracket model
        """
        self.assertEqual(self.bracket.name, 'My Test Bracket')
        self.assertEqual(self.bracket.slug, 'my-test-bracket')

    def test__generate_matches(self):
        """
        Test that we can generate a bracket from a list of players
        """
        players = mommy.make(Player, _quantity=16)

        self.bracket._generate_matches(players=players)

        self.assertEqual(Match.objects.filter(round=1).count(), 8)
        self.assertEqual(Match.objects.filter(round=2).count(), 4)
        self.assertEqual(Match.objects.filter(round=3).count(), 2)
        self.assertEqual(Match.objects.filter(round=4).count(), 1)

    def test_to_json(self):
        """
        Test that we can generate the JSON required by jQuery bracket
        """
        match_1 = mommy.make(Match, player_1_init=mommy.make(Player, name='p1'),
                                    player_2_init=mommy.make(Player, name='p2'),
                                    bracket=self.bracket, round=1, round_index=0,
                                    player_1_score=2, player_2_score=1)
        match_2 = mommy.make(Match, player_1_init=mommy.make(Player, name='p3'),
                                    player_2_init=mommy.make(Player, name='p4'),
                                    bracket=self.bracket, round=1, round_index=1,
                                    player_1_score=1, player_2_score=2)
        match_3 = mommy.make(Match, player_1_init=mommy.make(Player, name='p5'),
                                    player_2_init=mommy.make(Player, name='p6'),
                                    bracket=self.bracket, round=1, round_index=2,
                                    player_1_score=2, player_2_score=0)
        match_4 = mommy.make(Match, player_1_init=mommy.make(Player, name='p7'),
                                    player_2_init=mommy.make(Player, name='p8'),
                                    bracket=self.bracket, round=1, round_index=3,
                                    player_1_score=0, player_2_score=2)
        match_5 = mommy.make(Match, bracket=self.bracket, round=2, round_index=0,
                             previous_match_1=match_1, previous_match_2=match_2,
                             player_1_score=2, player_2_score=1)
        match_6 = mommy.make(Match, bracket=self.bracket, round=2, round_index=1,
                             previous_match_1=match_3, previous_match_2=match_4,
                             player_1_score=1, player_2_score=2)
        match_7 = mommy.make(Match, bracket=self.bracket, round=3, round_index=0,
                             previous_match_1=match_5, previous_match_2=match_6,
                             player_1_score=2, player_2_score=0)

        data = json.loads(self.bracket.to_json())
        self.assertEqual(data['teams'], [
            ['p1', 'p2'], ['p3', 'p4'], ['p5', 'p6'], ['p7', 'p8']
        ])
        self.assertEqual(data['results'],
            [                       # list of brackets
                [                   # list of rounds
                    [               # first round
                        [2,1],      # first matchup
                        [1,2],
                        [2,0],
                        [0,2]
                    ],
                    [               # second round
                        [2,1],
                        [1,2]
                    ],
                    [               # third round
                        [2,0]
                    ]
                ]
            ]
        )


class MatchTestCase(TestCase):

    def setUp(self):
        self.player_1 = mommy.make(Player)
        self.player_2 = mommy.make(Player)
        self.match = mommy.make(Match, player_1_init=self.player_1,
                                player_2_init=self.player_2)

    def test_match_basics_with_players(self):
        """
        Test the basic functionality of Match with Players
        """
        self.assertIsInstance(self.match.player_1_init, Player)
        self.assertIsInstance(self.match.player_2_init, Player)
        self.assertIsInstance(self.match.bracket, Bracket)

    def test_match_basics_with_matches(self):
        """
        Test the basic functionality of Match with previous matches
        """
        self.match.player_1_init = None
        self.match.player_2_init = None
        self.match.previous_match_1 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)
        self.match.previous_match_2 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)
        self.match.save()

        self.assertIsInstance(self.match.previous_match_1, Match)
        self.assertIsInstance(self.match.previous_match_2, Match)

    def test_match_player_1_init_requires_player_2_init(self):
        """
        Test that we raise an error if player_1 is defined but not player_2_init
        """
        self.match.player_2_init = None

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_player_2_init_requires_player_1(self):
        """
        Test that we raise an error if player_1 is defined but not player_2_init
        """
        self.match.player_1_init = None

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_previous_match_1_requires_previous_match_2(self):
        """
        Test that we raise an error if previous_match_1 is defined but not
        previous_match_2
        """
        self.match.player_1_init = None
        self.match.player_2_init = None
        self.match.previous_match_1 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_previous_match_2_requires_previous_match_1(self):
        """
        Test that we raise an error if previous_match_2 is defined but not
        previous_match_1
        """
        self.match.player_1_init = None
        self.match.player_2_init = None
        self.match.previous_match_2 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_must_set_players_or_matches(self):
        """
        Test that a Match must either have players or matches set
        """
        self.match.player_1_init = None
        self.match.player_2_init = None

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_cannot_set_players_and_match_1(self):
        """
        Test that a Match cannot have both players and match 1
        """
        self.match.previous_match_1 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_cannot_set_players_and_match_2(self):
        """
        Test that a Match cannot have both players and match 2
        """
        self.match.previous_match_2 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_cannot_set_player_1_init_and_match_1(self):
        """
        Test that a Match cannot have only player 1 and match 1
        """
        self.match.player_1_init = None
        self.match.previous_match_1 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_cannot_set_player_2_init_and_match_2(self):
        """
        Test that a Match cannot have only player 2 and match 2
        """
        self.match.player_2_init = None
        self.match.previous_match_2 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_cannot_set_player_2_init_and_match_1(self):
        """
        Test that a Match cannot have only player 2 and match 1
        """
        self.match.player_2_init = None
        self.match.previous_match_1 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_cannot_set_player_1_init_and_match_2(self):
        """
        Test that a Match cannot have only player 1 and match 2
        """
        self.match.player_1_init = None
        self.match.previous_match_2 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_cannot_set_players_and_matches(self):
        """
        Test that a Match cannot have both players and matches
        """
        self.match.previous_match_1 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)
        self.match.previous_match_2 = mommy.make(Match, player_1_init=self.player_1,
                                                 player_2_init=self.player_2)

        with self.assertRaises(ValidationError):
            self.match.save()

    def test_match_player_1_and_player_2(self):
        """
        Test that we return the player_1_init and player_2_init when we call
        player_1 and player_2
        """
        self.assertEqual(self.match.player_1, self.player_1)
        self.assertEqual(self.match.player_2, self.player_2)

    def test_winner_player_1(self):
        """
        Test that we can determine that player 1 is the winner of a Match
        """
        self.match.player_1_score = 2
        self.match.player_2_score = 1

        self.assertEqual(self.match.winner(), self.player_1)

    def test_winner_player_2(self):
        """
        Test that we can determine that player 2 is the winner of a Match
        """
        self.match.player_1_score = 1
        self.match.player_2_score = 2

        self.assertEqual(self.match.winner(), self.player_2)

    def test_winner_none(self):
        """
        Test that we return None when no winner can be determined
        """
        self.assertIsNone(self.match.winner())

    def test_player_1_is_winner_of_previous_match_1(self):
        """
        Test that Match.player_1 is evaluated to be the winner of
        Match.previous_match_1
        """
        self.match.player_1_score = 5
        self.match.player_2_score = 7
        match = Match(previous_match_1=self.match,
                      previous_match_2=mommy.make(Match,
                                                  player_1_init=mommy.make(Player),
                                                  player_2_init=mommy.make(Player)
        ))

        self.assertEqual(match.player_1, self.player_2)

    def test_player_2_is_winner_of_previous_match_2(self):
        """
        Test that Match.player_2 is evaluated to be the winner of
        Match.previous_match_2
        """
        self.match.player_1_score = 5
        self.match.player_2_score = 3
        match = Match(previous_match_1=mommy.make(Match,
                                                  player_1_init=mommy.make(Player),
                                                  player_2_init=mommy.make(Player)),
                      previous_match_2=self.match)

        self.assertEqual(match.player_2, self.player_1)
