insert_command = '''
    INSERT OR IGNORE INTO commands (name)
    VALUES (:name)
'''

get_command_id_query = '''
    SELECT id FROM channels
    WHERE command_id = :commandId
'''

insert_permitted = '''
    INSERT INTO channel_command_permissions
    ( channel_id, command_id, user_id )
    VALUES (:channelId,
            (SELECT id FROM commands WHERE name = :commandName),
            :userId)
'''

delete_permitted = '''
    DELETE FROM channel_command_permissions
    WHERE command_id = (SELECT id FROM commands WHERE name = :commandName) AND channel_id = :channelId
'''

check_permitted_query = '''
    SELECT * FROM channel_command_permissions
    WHERE channel_id = :channelId
    AND command_id = (SELECT id FROM commands WHERE name = :commandName)
'''

add_image_query = '''
    INSERT INTO images
    ( file_path, source )
    VALUES (:filePath, :source)
'''

add_tag_query = '''
    INSERT OR IGNORE INTO tags
    ( name )
    VALUES (:tagName)
'''

get_tag_id_query = '''
    SELECT id FROM tags
    WHERE name = :tagName
'''

get_tags_for_image_query = '''
    SELECT * FROM tags
    WHERE tag_id IN
    ( SELECT tag_id FROM tag_connections
      WHERE image_id = :imageId )
'''

get_images_with_tag_query = '''
    SELECT * FROM images
    WHERE image_id IN
    ( SELECT image_id FROM tag_connections
      WHERE tag_id = :tagId )
'''

add_tag_to_image_query = '''
    INSERT OR IGNORE INTO tag_connections
    ( image_id, tag_id )
    VALUES (:imageId, :tagId)
'''

remove_tag_from_image_query = '''
    DELETE FROM tag_connections
    WHERE image_id = :imageId
    AND tag_id = :tagId
'''
