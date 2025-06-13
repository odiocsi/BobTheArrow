import config
class HuLocale:
    def __init__(self):
        self.results = "Találatok"
        self.status = "Státusz"
        self.loading = "Betöltés..."
        self.searching = "Keresés..."
        self.musicplayer = "Zenelejátszó"
        self.playlist = "Lejátszási lista"
        self.rank = "Rank"
        self.winrate = "Győzelmi arány"
        self.matches = "Meccsek"
        self.hero = " hősök"
        self.alias = "Rövidítés: "
        self.description = "Leírás: "
        self.usage = "Használat: "

        self.message_deleted = " üzenet törölve."
        self.cant_use_here = "Ezt a parancsot itt nem használhatod."
        self.choose_song_first = "Először válaszd ki a zenét."
        self.join_voice_first = "Először lépj be egy hangcsatornába."
        self.not_in_voice = "A bot nincsen egy hangcsatornában sem."
        self.no_song_found = "Nem található zene a megadott kereséssel."
        self.not_implemented = "Nincs implementálva."
        self.name_required = "A név megadása kötelező."
        self.type_required = "A típus megadása kötelező."
        self.prefix_required = "A prefix megadása kötelező."
        self.message_required = "Az üzenet megadása kötelező."
        self.lang_required = "A nyelv megadása kötelező."
        self.welcome_message_set_to = "Az üdvözlő üzenet beállítva a következőre: "
        self.welcome_roles_set_to = "Az üdvözlő szerepkörök beállítva: "
        self.rank_required = "Meg kell adnod legalább egy rangot."
        self.word_required = "Meg kell adnod legalább egy szót."
        self.restricted_words_added = "A következő szavak rákerültek a tiltólistára: "
        self.restricted_words_removed = "A következő szavak lekerültek a tiltólistáról: "
        self.restricted_words_cleared = "A tiltólista törölve lett."
        self.title_required = "A cím megadása kötelező."
        self.message_moderated = "Az üzenet moderálva lett."
        self.no_perm = "A botnak nincsen joga a rang hozzáadásához!"
        self.error = "Hiba: "
        self.request_failed = "A kérés nem sikerült: "
        self.no_song_in_playlist = "Nincsen zene a lejátszási listában."
        self.current_song = "Jelenlegi zene"
        self.choose_a_song = "Válassz egy zenét a listából:"
        self.last_updated = "Utoljára frissítve"
        self.map_statistics = " pálya statisztikái"
        self.matchup_statistics = " matchup statisztikái"
        self.bot_commands = "Bot Parancsok"
        self.list_of_commands = "Az elérhető parancsok listája."
        self.wrong_lang = "Érvénytelen nyelv."
        self.lang_set = "A bot új nyelve: "

        self.prefix_max_char = "A prefix maximum 1 karakter lehet."
        self.prefix_set_to = "A prefix beállítva a következőre: "

        self.wrong_first_param = "Hibás paraméter."
        self.wrong_second_param = "Hibás 2. paraméter."
        self.wrong_third_param = "Hibás 3. paraméter."

        self.ranked_statistics = " rangsorolt statisztikái"
        self.private_profile = "A megadott profil privát"
        self.unexpected_error = "Váratlan hiba történt"
        self.profile_update_started = "A profil frissítése megkezdödött"

        self.music_set_to = "A zene csatorna beállítva a következőre: "
        self.music_channel_already_set = "A zene csatorna már be van állítva."
        self.music_channel_not_set = "Nincsen beállítva csatorna a zenelejátszóhoz."
        self.music_channel_deleted = "A zene csatorna törölve."

        self.lol_set_to = "A lol csatorna beállítva a következőre: "
        self.lol_channel_already_set = "A lol csatorna már be van állítva."
        self.lol_channel_not_set = "Nincsen beállítva csatorna a lol statisztikákhoz."
        self.lol_channel_deleted = "A lol csatorna törölve."

        self.rivals_set_to = "A rivals csatorna beállítva a következőre: "
        self.rivals_channel_already_set = "A rivals csatorna már be van állítva."
        self.rivals_channel_not_set = "Nincsen beállítva csatorna a rivals statisztikákhoz."
        self.rivals_channel_deleted = "A rivals csatorna törölve."

        self.welcome_set_to = "Az üdvözlő csatorna beállítva a következőre: "
        self.welcome_channel_already_set = "Az üdvözlő csatorna már be van állítva."
        self.welcome_channel_not_set = "Nincsen beállítva csatorna az üdvözlő üzenetekhez."
        self.welcome_channel_deleted = "Az üdvözlő csatorna törölve."


        self.started = "A bot elindult."
        self.stopped = "A bot leállt."
        self.token_missing = "Hiányzik a token."

        self.wrong_link = "Érvénytelen hivatkozás."
        self.error_delete_msg = "Az üzenet törlése sikertelen."
        self.error_delete_file = "A fájl törlése sikertelen."

        self.play_desc = "Zene lejátszása a csatornában."
        self.play_usage = "<cím/link/playlist>"

        self.lol_desc = "League of Legends statisztikák lekérése."
        self.lol_usage = ""

        self.rivals_desc = "Marvel Rivals statisztikák lekérése"
        self.rivals_usage = "<név> <szezon(0,1,1.5 ...)/update> <típus(üres,map,matchup)>"

        self.chat_desc = "Chat üzenetek törlése"
        self.chat_usage = "<üzenetszám>"

        self.set_channel_desc = "Csatorna beállítása egy specifikus üzenethez."
        self.set_channel_usage = "<típus(music,rivals,lol,welcome)>"

        self.clear_channel_desc = "Csatorna törlése egy specfikus üzenethez."
        self.clear_channel_usage = "<típus(music,rivals,lol,welcome)>"

        self.set_prefix_desc = "A bot előtagjának beállítása."
        self.set_prefix_usage = "<prefix>"

        self.set_welcome_msg_desc = "Üdvözlő üzenet beállítása."
        self.set_welcome_msg_usage = "<üzenet>"

        self.set_welcome_rls_desc = "Csatlakozási rangok beállítása."
        self.set_welcome_rls_usage = "<rangok>"

        self.system_message_desc = "Rendszerüzenet küldése."
        self.system_message_usage = "<cím> <üzenet> (többsoroshoz: \\n)"

        self.add_restricted_desc = "Tiltott szó hozzáadása."
        self.add_restricted_usage = "<szavak>"

        self.remove_restricted_desc = "Tiltott szó törlése."
        self.remove_restricted_usage = "<szavak>"

        self.clear_restricted_desc = "Tiltott szavak törlése."
        self.clear_restricted_usage = ""

        self.set_language_desc = "A bot nyelvének beállítása."
        self.set_language_usage = "<nyelv("

        self.join_desc = "Csatlakozás egy hangcsatornához."
        self.join_usage = ""

        self.leave_desc = "Lecsatlakozás egy hangcsatornáról."
        self.leave_usage = ""


class EnLocale:
    def __init__(self):
        self.results = "Results"
        self.status = "Status"
        self.loading = "Loading..."
        self.searching = "Searching..."
        self.musicplayer = "Music Player"
        self.playlist = "Playlist"
        self.rank = "Rank"
        self.winrate = "Winrate"
        self.matches = "Matches"
        self.hero = " heroes"
        self.alias = "Alias: "
        self.description = "Description: "
        self.usage = "Usage: "

        self.message_deleted = " message deleted."
        self.cant_use_here = "You can't use this command here."
        self.choose_song_first = "Please choose a song first."
        self.join_voice_first = "Please join a voice channel first."
        self.not_in_voice = "The bot is not in any voice channel."
        self.no_song_found = "No song found with the given search."
        self.not_implemented = "Not implemented."
        self.name_required = "Name is required."
        self.type_required = "Type is required."
        self.prefix_required = "Prefix is required."
        self.message_required = "Message is required."
        self.welcome_message_set_to = "Welcome message set to: "
        self.welcome_roles_set_to = "Welcome roles set to: "
        self.rank_required = "You need to provide at least one rank."
        self.word_required = "You need to provide at least one word."
        self.restricted_words_added = "The following words have been added to the blacklist: "
        self.restricted_words_removed = "The following words have been removed from the blacklist: "
        self.restricted_words_cleared = "The blacklist has been cleared."
        self.title_required = "Title is required."
        self.lang_required = "Lang is required."
        self.message_moderated = "The message has been moderated."
        self.no_perm = "The bot doesn't have permission to add ranks!"
        self.error = "Error: "
        self.request_failed = "The request failed: "
        self.no_song_in_playlist = "There is no song in the playlist."
        self.current_song = "Current song"
        self.choose_a_song = "Choose a song from the list:"
        self.last_updated = "Last updated"
        self.map_statistics = " map statistics"
        self.matchup_statistics = " matchup statistics"
        self.bot_commands = "Bot Commands"
        self.list_of_commands = "List of available commands."
        self.wrong_lang = "Wrong language."
        self.lang_set = "The new language is: "

        self.prefix_max_char = "Prefix can only be 1 character."
        self.prefix_set_to = "Prefix set to: "

        self.wrong_first_param = "Incorrect parameter."
        self.wrong_second_param = "Incorrect 2nd parameter."
        self.wrong_third_param = "Incorrect 3rd parameter."

        self.ranked_statistics = " ranked statistics"
        self.private_profile = "The given profile is private"
        self.unexpected_error = "An unexpected error occurred"
        self.profile_update_started = "Profile update started"

        self.music_set_to = "Music channel set to: "
        self.music_channel_already_set = "Music channel is already set."
        self.music_channel_not_set = "No channel set for the music player."
        self.music_channel_deleted = "Music channel deleted."

        self.lol_set_to = "LOL channel set to: "
        self.lol_channel_already_set = "LOL channel is already set."
        self.lol_channel_not_set = "No channel set for LOL statistics."
        self.lol_channel_deleted = "LOL channel deleted."

        self.rivals_set_to = "Rivals channel set to: "
        self.rivals_channel_already_set = "Rivals channel is already set."
        self.rivals_channel_not_set = "No channel set for Rivals statistics."
        self.rivals_channel_deleted = "Rivals channel deleted."

        self.welcome_set_to = "Welcome channel set to: "
        self.welcome_channel_already_set = "Welcome channel is already set."
        self.welcome_channel_not_set = "No channel set for welcome messages."
        self.welcome_channel_deleted = "Welcome channel deleted."

        self.started = "The bot has started."
        self.stopped = "The bot has stopped."
        self.token_missing = "Token is missing."

        self.wrong_link = "Invalid link."
        self.error_delete_msg = "Failed to delete the message."
        self.error_delete_file = "Failed to delete the file."

        self.play_desc = "Play music in the channel."
        self.play_usage = "<title/link/playlist>"

        self.lol_desc = "Fetch League of Legends statistics."
        self.lol_usage = ""

        self.rivals_desc = "Fetch Marvel Rivals statistics"
        self.rivals_usage = "<name> <season(0,1,1.5 ...)/update> <type(empty,map,matchup)>"

        self.chat_desc = "Delete chat messages"
        self.chat_usage = "<number_of_messages>"

        self.set_channel_desc = "Set channel for a specific message."
        self.set_channel_usage = "<type(music,rivals,lol,welcome)>"

        self.clear_channel_desc = "Clear channel for a specific message."
        self.clear_channel_usage = "<type(music,rivals,lol,welcome)>"

        self.set_prefix_desc = "Set the bot prefix."
        self.set_prefix_usage = "<prefix>"

        self.set_welcome_msg_desc = "Set welcome message."
        self.set_welcome_msg_usage = "<message>"

        self.set_welcome_rls_desc = "Set welcome roles."
        self.set_welcome_rls_usage = "<roles>"

        self.system_message_desc = "Send system message."
        self.system_message_usage = "<title> <message> (for multiline: \\n)"

        self.add_restricted_desc = "Add a restricted word."
        self.add_restricted_usage = "<words>"

        self.remove_restricted_desc = "Remove a restricted word."
        self.remove_restricted_usage = "<words>"

        self.clear_restricted_desc = "Clear restricted words."
        self.clear_restricted_usage = ""

        self.set_language_desc = "Change the language of the bot."
        self.set_language_usage = "<lang("

        self.join_desc = "Join a voice channel."
        self.join_usage = ""

        self.leave_desc = "Leave a voice channel."
        self.leave_usage = ""

hu = HuLocale()
en = EnLocale()
locales = {
    "hu": hu,
    "en": en,
}

def get_dict(lang):
    return locales.get(lang, config.default_lang)

def key_exists(key):
    if key in locales:
        return True
    return False

def get_keys():
    return list(locales.keys())