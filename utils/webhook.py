from discord_webhook import DiscordWebhook, DiscordEmbed


def send_webhook(data):
    embed = DiscordEmbed(title=data['name'], url=f"https://sell.wethenew.com/consignment/product/{data['id']}", color=242424)
    embed.set_thumbnail(url=data['image'])

    sizes_str = '\n'.join(data['sizes'])
    sizes = [size.replace(' EU', '') for size in sizes_str.split('\n')]
    clean_sizes = '\n'.join(sizes)
    embed.add_embed_field(name="Sizes", value=clean_sizes, inline=False)
    embed.set_timestamp()

    webhook = DiscordWebhook(url='URL')
    webhook.add_embed(embed)
    webhook.execute()
