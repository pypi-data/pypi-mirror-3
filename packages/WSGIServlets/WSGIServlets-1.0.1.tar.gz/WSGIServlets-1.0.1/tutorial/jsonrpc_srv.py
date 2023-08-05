# -*- python -*-

## Copyright 2011 Daniel J. Popowich
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import random

from wsgiservlets import JSONRPCServer

class jsonrpc_srv(JSONRPCServer):

    def rpc_quote(self):
        play = random.choice(PLAYS)
        quote = random.choice(QUOTES[play])
        return quote, play








# -*-*- DOC -*-*-

QUOTES = {
'Sonnet 18' : [
'''
"Shall I compare thee to a summer's day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer's lease hath all too short a date".'''],

'Hamlet' : [

'''To be, or not to be: that is the question". - (Act III, Scene I).''',

'''"Neither a borrower nor a lender be; For loan oft loses both itself and friend, and borrowing dulls the edge of husbandry". - (Act I, Scene III).''',

'''"This above all: to thine own self be true". - (Act I, Scene III).''',

'''"Though this be madness, yet there is method in 't.". - (Act II, Scene II).''',

'''"That it should come to this!". - (Act I, Scene II).''',

'''"There is nothing either good or bad, but thinking makes it so". - (Act II, Scene II).''',

'''"What a piece of work is man! how noble in reason! how infinite in faculty! in form and moving how express and admirable! in action how like an angel! in apprehension how like a god! the beauty of the world, the paragon of animals! ". - (Act II, Scene II).''',

'''"The lady doth protest too much, methinks". - (Act III, Scene II).''',

'''"In my mind's eye". - (Act I, Scene II).''',

'''"A little more than kin, and less than kind". - (Act I, Scene II).''',

'''"The play 's the thing wherein I'll catch the conscience of the king". - (Act II, Scene II).''',

'''"And it must follow, as the night the day, thou canst not then be false to any man". - (Act I, Scene III)."This is the very ecstasy of love". - (Act II, Scene I).''',

'''"Brevity is the soul of wit". - (Act II, Scene II).''',

'''"Doubt that the sun doth move, doubt truth to be a liar, but never doubt I love". - (Act II, Scene II).''',

'''"Rich gifts wax poor when givers prove unkind". - (Act III, Scene I).''',

'''"Do you think I am easier to be played on than a pipe?" - (Act III, Scene II).''',

'''"I will speak daggers to her, but use none". - (Act III, Scene II).''',

'''"When sorrows come, they come not single spies, but in battalions". - (Act IV, Scene V).''',],

'As You Like It' : [

'''"All the world 's a stage, and all the men and women merely players. They have their exits and their entrances; And one man in his time plays many parts" - (Act II, Scene VII).''',

'''"Can one desire too much of a good thing?". - (Act IV, Scene I).''',

'''"I like this place and willingly could waste my time in it" - (Act II, Scene IV).''',

'''"How bitter a thing it is to look into happiness through another man's eyes!" - (Act V, Scene II).''',

'''"Blow, blow, thou winter wind! Thou art not so unkind as man's ingratitude".(Act II, Scene VII).''',

'''"True is it that we have seen better days". - (Act II, Scene VII).''',

'''"For ever and a day". - (Act IV, Scene I).''',

'''"The fool doth think he is wise, but the wise man knows himself to be a fool". - (Act V, Scene I).'''],

'King Richard III' : [

'''"Now is the winter of our discontent". - (Act I, Scene I).''',

'''"A horse! a horse! my kingdom for a horse!". - (Act V, Scene IV).''',

'''"Conscience is but a word that cowards use, devised at first to keep the strong in awe". - (Act V, Scene III).''',

'''"So wise so young, they say, do never live long". - (Act III, Scene I).''',

'''"Off with his head!" - (Act III, Scene IV).''',

'''"An honest tale speeds best, being plainly told". - (Act IV, Scene IV).''',

'''"The king's name is a tower of strength". - (Act V, Scene III).''',

'''"The world is grown so bad, that wrens make prey where eagles dare not perch". - (Act I, Scene III).'''],

'Romeo and Juliet' : [

'''"O Romeo, Romeo! wherefore art thou Romeo?". - (Act II, Scene II).''',

'''"It is the east, and Juliet is the sun" . - (Act II, Scene II).''',

'''"Good Night, Good night! Parting is such sweet sorrow, that I shall say good night till it be morrow." - (Act II, Scene II).''',

'''"What's in a name? That which we call a rose by any other name would smell as sweet". - (Act II, Scene II).''',

'''"Wisely and slow; they stumble that run fast". - (Act II, Scene III).''',

'''"Tempt not a desperate man". - (Act V, Scene III).''',

'''"For you and I are past our dancing days" . - (Act I, Scene V).''',

'''"O! she doth teach the torches to burn bright". - (Act I, Scene V).''',

'''"It seems she hangs upon the cheek of night like a rich jewel in an Ethiope's ear" . - (Act I, Scene V).''',

'''"See, how she leans her cheek upon her hand! O that I were a glove upon that hand, that I might touch that cheek!". - (Act II, Scene II).''',

'''"Not stepping o'er the bounds of modesty". - (Act IV, Scene II).''',],

'The Merchant of Venice' : [

'''"But love is blind, and lovers cannot see".''',

'''"If you prick us, do we not bleed? if you tickle us, do we not laugh? if you poison us, do we not die? and if you wrong us, shall we not revenge?". - (Act III, Scene I).''',

'''"The devil can cite Scripture for his purpose". - (Act I, Scene III).''',

'''"I like not fair terms and a villain's mind". - (Act I, Scene III).'''],

'The Merry Wives of Windsor' : [

'''"Why, then the world 's mine oyster" - (Act II, Scene II).''',

'''"This is the short and the long of it". - (Act II, Scene II).''',

'''"I cannot tell what the dickens his name is". - (Act III, Scene II).''',

'''"As good luck would have it". - (Act III, Scene V).'''],

'Measure for Measure' : [

'''"Our doubts are traitors, and make us lose the good we oft might win, by fearing to attempt". - (Act I, Scene IV).''',

'''"Some rise by sin, and some by virtue fall". - (Act II, Scene I).''',

'''"The miserable have no other medicine but only hope". - (Act III, Scene I).'''],

'King Henry IV, Part I' : [

'''"He will give the devil his due". - (Act I, Scene II).''',

'''"The better part of valour is discretion". - (Act V, Scene IV).''',],

'King Henry IV, Part II' : [

'''"He hath eaten me out of house and home". - (Act II, Scene I).''',

'''"Uneasy lies the head that wears a crown". - (Act III, Scene I).''',

'''"A man can die but once". - (Act III, Scene II).''',

'''"I do now remember the poor creature, small beer". - (Act II, Scene II).''',

'''"We have heard the chimes at midnight". - (Act III, Scene II)''',],

'King Henry IV, Part III' : [

'''"The smallest worm will turn, being trodden on". - (Act II, Scene II).''',

'''"Suspicion always haunts the guilty mind; The thief doth fear each bush an officer". - (Act V, Scene VI).''',],

'King Henry the Sixth, Part I' : [

'''"Delays have dangerous ends". - (Act III, Scene II).''',

'''"Of all base passions, fear is the most accursed". - (Act V, Scene II).''',],

'King Henry the Sixth, Part II' : [

'''"The first thing we do, let's kill all the lawyers". - (Act IV, Scene II).''',

'''"Small things make base men proud". - (Act IV, Scene I).''',

'''"True nobility is exempt from fear". - (Act IV, Scene I).''',],

'King Henry the Sixth, Part III' : [

'''"Having nothing, nothing can he lose".- (Act III, Scene III).''',],

'Taming of the Shrew' : [

'''"I 'll not budge an inch". - (Induction, Scene I).''',],

'Timon of Athens' : [

'''"We have seen better days". - (Act IV, Scene II).''',],

'Julius Caesar' : [

'''"Friends, Romans, countrymen, lend me your ears; I come to bury Caesar, not to praise him". - (Act III, Scene II).''',

'''"But, for my own part, it was Greek to me". - (Act I, Scene II).''',

'''"A dish fit for the gods". - (Act II, Scene I).''',

'''"Cry "Havoc," and let slip the dogs of war". - (Act III, Scene I).''',

'''"Et tu, Brute!" - (Act III, Scene I).''',

'''"Men at some time are masters of their fates: The fault, dear Brutus, is not in our stars, but in ourselves, that we are underlings". - (Act I, Scene II).''',

'''"Not that I loved Caesar less, but that I loved Rome more". - (Act III, Scene II).''',

'''"Beware the ides of March". - (Act I, Scene II).''',

'''"This was the noblest Roman of them all". - (Act V, Scene V).''',

'''"When that the poor have cried, Caesar hath wept: Ambition should be made of sterner stuff". - (Act III, Scene II).''',

'''"Yond Cassius has a lean and hungry look; He thinks too much: such men are dangerous". (Act I, Scene II).''',

'''"For Brutus is an honourable man; So are they all, all honourable men". - (Act III, Scene II).''',

'''"As he was valiant, I honor him; but, as he was ambitious, I slew him" . - (Act III, Scene II).''',

'''"Cowards die many times before their deaths; The valiant never taste of death but once.,
Of all the wonders that I yet have heard, it seems to me most strange that men should fear;
Seeing that death, a necessary end, will come when it will come". - (Act II, Scene II).''',],


'Macbeth' : [

'''"There 's daggers in men's smiles". - (Act II, Scene III).''',

'''"what 's done is done".- (Act III, Scene II).''',

'''"I dare do all that may become a man; Who dares do more is none". - (Act I, Scene VII).''',

'''"Fair is foul, and foul is fair". - (Act I, Scene I).''',

'''"I bear a charmed life". - (Act V, Scene VIII).''',

'''"Yet do I fear thy nature; It is too full o' the milk of human kindness." - (Act I, Scene V).''',

'''"Will all great Neptune's ocean wash this blood clean from my hand? No, this my hand will rather the multitudinous seas incarnadine, making the green one red" - (Act II, Scene II).''',

'''"Double, double toil and trouble; Fire burn, and cauldron bubble." - (Act IV, Scene I).''',

'''"Out, damned spot! out, I say!" - (Act V, Scene I)..''',

'''"All the perfumes of Arabia will not sweeten this little hand." - (Act V, Scene I).''',

'''"When shall we three meet again in thunder, lightning, or in rain? When the hurlyburly 's done,
When the battle 's lost and won". - (Act I, Scene I).
''',

'''"If chance will have me king, why, chance may crown me". - (Act I, Scene III).''',

'''"Nothing in his life became him like the leaving it; he died as one that had been studied in his death to throw away the dearest thing he owed, as 't were a careless trifle". - (Act I, Scene IV).''',

'''"Look like the innocent flower, but be the serpent under 't." - (Act I, Scene V).''',

'''"I have no spur to prick the sides of my intent, but only vaulting ambition, which o'erleaps itself, and falls on the other." - (Act I, Scene VII).''',

'''"Is this a dagger which I see before me, The handle toward my hand?" - (Act II, Scene I).''',

'''"Out, out, brief candle! Life's but a walking shadow, a poor player that struts and frets his hour upon the stage and then is heard no more: it is a tale told by an idiot, full of sound and fury, signifying nothing." - (Act V, Scene V).''',],

'King Lear' : [

'''"How sharper than a serpent's tooth it is to have a thankless child!" - (Act I, Scene IV).''',

'''"I am a man more sinned against than sinning". - (Act III, Scene II).''',

'''"My love's more richer than my tongue". - (Act I, Scene I).''',

'''"Nothing will come of nothing." - (Act I, Scene I).''',

'''"Have more than thou showest, speak less than thou knowest, lend less than thou owest". - (Act I, Scene IV).''',

'''"The worst is not, So long as we can say, 'This is the worst.' " . - (Act IV, Scene I).''',],

'Othello' : [

'''"T'is neither here nor there." - (Act IV, Scene III).''',

'''"I will wear my heart upon my sleeve for daws to peck at". - (Act I, Scene I).''',

'''"To mourn a mischief that is past and gone is the next way to draw new mischief on". - (Act I, Scene III).''',

'''"The robbed that smiles steals something from the thief". - (Act I, Scene III).''',],

'Antony and Cleopatra' : [

'''"My salad days, when I was green in judgment." - (Act I, Scene V).''',],

'Cymbeline' : [

'''"The game is up." - (Act III, Scene III).''',

'''"I have not slept one wink.". - (Act III, Scene III).''',],

'Twelfth Night' : [

'''"Be not afraid of greatness: some are born great, some achieve greatness and some have greatness thrust upon them". - (Act II, Scene V).''',

'''"Love sought is good, but giv'n unsought is better" . - (Act III, Scene I).''',],

'The Tempest' : [

'''"We are such stuff as dreams are made on, rounded with a little sleep".''',],

'King Henry the Fifth' : [

'''"Men of few words are the best men" . - (Act III, Scene II).''',],

'''A Midsummer Night's Dream''' : [

'''"The course of true love never did run smooth". - (Act I, Scene I).''',

'''"Love looks not with the eyes, but with the mind, and therefore is winged Cupid painted blind". - (Act I, Scene I).''',],

'Much Ado About Nothing' : [

'''"Everyone can master a grief but he that has it". - (Act III, Scene II).''',],

'Titus Andronicus' : [

'''"These words are razors to my wounded heart". - (Act I, Scene I).''',],

'''The Winter's Tale''' : [

'''"What 's gone and what 's past help should be past grief" . - (Act III, Scene II).''',

'''"You pay a great deal too dear for what's given freely". - (Act I, Scene I).''',],

'Taming of the Shrew' : [

'''"Out of the jaws of death". - (Act III, Scene IV).''',

'''"Thus the whirligig of time brings in his revenges". - (Act V, Scene I).''',

'''"For the rain it raineth every day". - (Act V, Scene I).''',],

'Troilus and Cressida' : [

'''"The common curse of mankind, - folly and ignorance". - (Act II, Scene III).''',],

'Coriolanus' : [

'''"Nature teaches beasts to know their friends". - (Act II, Scene I). ''']
}

PLAYS = QUOTES.keys()


# For use with mod_wsgi
application = jsonrpc_srv()
