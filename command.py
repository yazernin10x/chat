# Vérification du type de commande
if message.startswith("/"):
    command = message.split(" ")[0].lower()
    
    # Message privé
    if command == "/pm":
        # ... code existant ...
    
    # Effacer l'écran pour l'utilisateur
    elif command == "/clear":
        await self.send_json({
            "type": "clear_chat",
            "username": self.user.username
        })
        return
    
    # Afficher la liste des commandes
    elif command == "/help":
        help_message = """
        Commandes disponibles:
        /pm [utilisateur] [message] - Envoyer un message privé
        /clear - Effacer l'écran de chat
        /me [action] - Décrire une action
        /roll [nombre] - Lancer un dé
        /online - Voir qui est en ligne
        /help - Afficher cette aide
        """
        await self.send_json({
            "type": "system_message",
            "message": help_message
        })
        return
    
    # Action personnelle
    elif command == "/me":
        action = message[4:].strip()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "action_message",
                "username": self.user.username,
                "action": action
            }
        )
        return
    
    # Lancer un dé
    elif command == "/roll":
        try:
            max_number = int(message.split(" ")[1]) if len(message.split(" ")) > 1 else 6
            result = random.randint(1, max_number)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "dice_roll",
                    "username": self.user.username,
                    "result": result,
                    "max": max_number
                }
            )
        except ValueError:
            await self.send_json({
                "type": "error_message",
                "message": "Usage: /roll [nombre]"
            })
        return
    
    # Voir les utilisateurs en ligne
    elif command == "/online":
        online_users = [user.username for user in self.room.members.all() if user.is_online]
        await self.send_json({
            "type": "system_message",
            "message": f"Utilisateurs en ligne: {', '.join(online_users)}"
        })
        return