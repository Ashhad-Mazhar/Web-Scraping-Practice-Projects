import os
import pandas as pd
from config import CSV_FILE_PATH, IMAGES_PATH

class DataStorage:
    def save(self, records: list[dict]) -> None:
        if self.store_images(records, IMAGES_PATH):
            print('Images have been written to disk')
        else:
            print('There was an error while writing images to disk')
        if self.store_in_csv(records, CSV_FILE_PATH):
            print('Data has been written to csv')
        else:
            print('There was an error while writing data to csv')
    
    def store_images(self, records: list[dict], dir_name: str) -> None:
        '''
        Stores images according to player names in the specified directory
        name in the current path
        '''
        try:
            dir_path = os.path.join(os.path.curdir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            for record in records:
                image_data = record['player_image']['data']
                image_filename = record['player_image']['filename']
                try:
                    with open(os.path.join(dir_path, image_filename), 'wb') as file:
                        file.write(image_data)
                except:
                    print(f'Error while writing to image file: {image_filename}')
            return True
        except:
            return False
        
    def store_in_csv(self, records: list[dict], filepath: str) -> None:
        '''
        Stores the given records in a csv file
        '''
        try:
            df = pd.DataFrame.from_dict(records)
            # Dropping images as they have already been written on disk
            df.drop(columns=['player_image'], inplace=True)
            df.index = range(1, len(df) + 1)
            df.index.name = 'transfer_id'

            df.to_csv(filepath, index=True)
            return True
        except:
            return False