def format_help(stuff_list: list) -> list:
    for index, message in enumerate(stuff_list):
        stuff_content = message.get('content') or None
        stuff_embeds = message.get('embeds') or []
        stuff_files = message.get('files') or []

        if not (stuff_content or stuff_embeds or stuff_files):
            stuff_content = "This message is empty"

        new_stuff = {'content': stuff_content, 'embeds': stuff_embeds, 'files': stuff_files}
        stuff_list[index] = new_stuff
    
    return stuff_list
