# Death-by-the-Second
Death location parsing. Uncomment the bottom line to test it out! Additionally, you can find a product with 60 second intervals over the course of one bucket of games here: https://drive.google.com/file/d/0B3Wig6ukVmdlREEySDYydHBMRHc/view?usp=sharing

The main_parse method iterates over a list of match IDs, and then subsequently map out the deaths based on the specified interval stated by using the draw_deaths method. For aesthetics sake, deaths persist past a single frame, and can span to 3 frames. Given a time in epoch seconds which works with the URF endpoint, a number of runs, and an interval (default to 1 minute), the call to main_parse will create a .swf of the deaths in the bucket.

Death by the Second isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.
