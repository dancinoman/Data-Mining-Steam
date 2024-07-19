# Steam Class is used to import csv and cleaning data ready to explore
import os
from os import listdir
import pandas as pd
from termcolor import cprint
from sklearn.impute import SimpleImputer
import time
import colorama 

previous_progress = 0

class Steam:
    
    
    
    '''Import CSV to merge and transform data ready to explore
    '''
    def progress_bar(self, progress, msg = '', reset = False):
        global previous_progress
        
        if progress == 0: previous_progress = 0
        
        # Progress bar has 50 positions
        p2 = '█'
        empty = '-'
                    
        
        if progress < 50:
            
            while previous_progress != progress + 1:

                percent = 50 * (previous_progress/float(50))
                cha = (p2 * int(percent))
                bar = cha + empty * (50 - int(percent))
                print(colorama.Fore.YELLOW + "" + f"{msg}" + ''.rjust(40 - len(msg),'.') + f"|{bar}|", end = '\r' )
                previous_progress += 1
                time.sleep(0.07)
        else:
            bar = p2 * progress
            print(colorama.Fore.GREEN + "" + f"{msg}" + ''.rjust(40 - len(msg),'.') + f"|{bar}|")
       
        
    def get_data(self, name = ''):
        
        """
        A very flexible function that returns content of csv file in folder whatever the content has.
        1. Retrieve all csv files in Data/CSV/... folder and return a pack Dictionnary
        2. Or use name argument to get one csv file and return 1 Data frame

           name: string, default ''
                 name of csv in csv folder without extension. It returns one dataframe.
                 If there is nothing specified it returns all content of csv folder in a
                 dictionary.

           Method:
               get_data('name_of_csv_file') return (pandas.core.frame.DataFrame)


        """

        path = os.path.dirname(os.path.dirname(__file__)) + '/csv/'
        
        
        if not name:
            #Filter content of folder to get only csv files with extensions
            list_csv_files = [file for file in listdir(path) if 'Zone' not in file]

            #Filter csv files to get a name without extension
            list_csv_name = [name.replace('.csv', '') for name in list_csv_files]

            #Pack all csv data into a dictionnary
            csv_dict = {}
            for key, file in zip(list_csv_name,list_csv_files):
                csv_dict[key] = pd.read_csv(path + file)

            return csv_dict

        try:
            return pd.read_csv(path + name + '.csv')
        except FileNotFoundError:
            print('Error: No file found from your argument. Review your spelling or check if file exists please.')


    def get_three_dataset_game_price(self):
        """
        The function returns 3 merged dataframe from reviews, game details and popularity sale data frame based on sale volume
        >>> dataframe = Review game + Top games <2003-2023> + Game's details <2003-2023>
        """
        self.progress_bar(0, 'Loading dataframes:')
        
        data_detail = self.get_data('games_details')
        data_reviews = self.get_data('reviews')
        
        self.progress_bar(20,'Merging details and review score:')       
        
        # Grouping the games duplicates together
     
        reviews = data_reviews.groupby(['app_id'], as_index = False)[['review_score', 'review_votes']].mean()
        steam_games = data_detail.merge(
                                            reviews, 
                                            left_on = 'AppID', 
                                            right_on = 'app_id', 
                                            how='inner'
                                         )
        
        self.progress_bar(30, 'Cleaning:')
        steam_games = steam_games.drop(columns = 'app_id').rename(columns = {'AppID': 'app_id'})
        steam_games['Release date'] = pd.to_datetime(steam_games['Release date'])
        
        # Drop all empty data
        columns_to_drop = [
            'Reviews',
            'Website',
            'Support url', 
            'Support email', 
            'Metacritic url', 
            'Score rank', 
            'Notes', 
            'Screenshots', 
            'Movies'
        ]
        
        self.progress_bar(45, 'Merging top games:')
        steam_games = steam_games.drop(columns= columns_to_drop)
        
        # Games detail has 1997 to 2023 games with 9300 entries
        # Drop empty Developpers, Categories, Genres
        # Lost 300 entries after cleaning, the result is around 9100 entries
        
        steam_games = steam_games.dropna()
        
        # After inner merging, did not lost entries
        steam_games = steam_games.merge(
            self.get_top_games(inner_load = True)[['name','price']], 
            left_on=['Name'], 
            right_on =['name'], 
            how = 'left'
        ).drop(columns = 'name')
        
        self.progress_bar(50, 'Completed:')
        return steam_games

    def get_top_games(self, inner_load = False):
        """
        Get compatible dataframe from all in cv folder(games_top_<year>).
        Filter lacking information in dataframe or impute missing values.
        And return a concatenated dataframe together of all years avalaible.

        """
        if not inner_load: self.progress_bar(0,'Loading data')
        data = self.get_data()

        i = 0
        if not inner_load: self.progress_bar(20,'Concatenating data')
        # Concatenate all dataframe of games by year
        for name, df in data.items():
            if 'games_top' in name:
                # Adding the year that is missing to the dataframe
                df['release date'] += ' ' + name[10:]
                if i == 0:
                    games_top = df
                else:
                    games_top = pd.concat([games_top, df], axis= 0)

            i+= 1

        # 1. drop the followers with missing values at 40% because we might afford it
        # 2. drop the rating because it had only 3%
        # 3. impute the price because it had about a bit less than 30% missing value
        # 4. convert number object into numeric
        # 5. convert date to date
        if not inner_load: self.progress_bar(35,'Cleaning')
            
        games_top = games_top[games_top['followers'] != '—']
        games_top = games_top[games_top['rating'] != '—']
        games_top['price'].replace(to_replace= '—', value = 0, inplace= True)
        games_top['name'] = games_top['name'].apply(lambda x: x.lower())

        imputer = SimpleImputer(strategy="median", fill_value= 0)
        imputer.fit(games_top[['price']])
        games_top['price'] = imputer.transform(games_top[['price']])
        cols = ['rating', 'followers', 'max peak']
        games_top[cols] = games_top[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        games_top['release date'] = pd.to_datetime(games_top['release date'])
        
        # Finish and display it
        if not inner_load: self.progress_bar(50,'Completed')
            
        return games_top
 