import os
import pandas as pd
from config import CSV_FILENAME, IMAGES_PATH

class DataStorage:
    def save(self, records: list[dict]) -> None:
        if self.store_images(records, IMAGES_PATH):
            print('Images have been written to disk')
        else:
            print('There was an error while writing images to disk')
        if self.store_in_csv(records, CSV_FILENAME):
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
        Applies some transformations to the given list of records, sorts
        it according to the transfer fee and then stores it in a csv file
        '''
        try:
            df = pd.DataFrame.from_dict(records)
            # Dropping images as they have already been written on disk
            df.drop(columns=['player_image'], inplace=True)
            # Transforming values like "€100.23m" into "100230000"
            df['player_value_in_euros'] = (df['player_value_in_euros']
                    .str.replace('€', '')
                    .str.replace('.', '')
                    .str.replace('m', '0000')
            )
            df['transfer_fee_in_euros'] = (df['transfer_fee_in_euros']
                    .str.replace('€', '')
                    .str.replace('.', '')
                    .str.replace('m', '0000')
            )
            # Converting transfer fees to numeric so sorting
            # is done correctly
            df['transfer_fee_in_euros'] = pd.to_numeric(
                df['transfer_fee_in_euros'], errors='coerce'
            )
            df.sort_values('transfer_fee_in_euros', ascending=False, inplace=True)
            df.index = range(1, len(df) + 1)
            df.index.name = 'transfer_id'

            df.to_csv(filepath, index=True)
            return True
        except:
            return False