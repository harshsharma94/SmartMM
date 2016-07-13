import pickle
import operator
from utilities import id_to_recodetails

class Recommender:
    def get_n_recommendations(self,n,movie_lst):
        #Create User Profile
        #The no_of_feature will vary depending on testing

        no_of_feature = 5
        no_of_movies=10
        user_profile = dict()
        user_profile['genres']=dict()
        user_profile['directors']=dict()
        user_profile['cast']=dict()
        user_profile['writers']=dict()
        recommendation_list = []
        user_movie_list = []

        for mov_id,imdb_id,mov_name in movie_lst:
            try:
                #fetched_movies=ia.search_movie(line)
                #movie_id=fetched_movies[0].movieID
                #mov_details = prep_mov_details_dict(mov_to_id(line))
                mov_info = id_to_recodetails(mov_id)
                print mov_info
                user_movie_list.append(mov_info)

                print mov_info['name']

                for i in mov_info['genres']:
                    if user_profile['genres'].has_key(i):
                        user_profile['genres'][i] = user_profile['genres'][i] + 1
                    else:
                        user_profile['genres'][i] = 1

                for i in mov_info['directors']:
                    if user_profile['directors'].has_key(i):
                        user_profile['directors'][i] = user_profile['directors'][i] + 1
                    else:
                        user_profile['directors'][i] = 1

                for i in mov_info['writers']:
                    if user_profile['writers'].has_key(i):
                        user_profile['writers'][i] = user_profile['writers'][i] + 1
                    else:
                        user_profile['writers'][i] = 1

                for i in mov_info['cast']:
                    if user_profile['cast'].has_key(i):
                        user_profile['cast'][i] = user_profile['cast'][i] + 1
                    else:
                        user_profile['cast'][i] = 1
            except:
                pass
        count = 0
        key_error = 0
        similarity_value = {}
        with open("temp1.p","rb") as input_file:
            while 1:
                try:
                    movie_list= []
                    # Need to change to standard naming - massive source of bug
                    movie_list.append(pickle.load(input_file))
                    count +=1
                    #Similarity function
                    for movie in movie_list:
                        score = 0
                        clone_movie = {}
                        try:
                            clone_movie["genre"] = movie["genre"]

                            director_list = []
                            director_list  = [d["long imdb canonical name"] for d in movie["director"]]
                            clone_movie["director"] = director_list

                            cast_list = []
                            cast_list = [str(c["long imdb canonical name"].encode("utf-8")) for c in movie["cast"]]
                            clone_movie["cast"] = cast_list

                            writer_list = []
                            writer_list = [str(w["long imdb canonical name"].encode("utf-8")) for w in movie["writer"]]
                            clone_movie["writer"] = writer_list

                            clone_movie["rating"] = movie["rating"]


                            common_genre=set(user_profile['genres']).intersection(clone_movie['genre'])
                        #traverse the set and add the values of occurence total movies considered for creating user profile
                            temp_score=0
                            for i in common_genre:
                                temp_score=temp_score+user_profile['genres'][i]
                            score=score+ 0.0123 * ((temp_score*1.0/no_of_movies)/no_of_feature)

                            common_director=set(user_profile['directors']).intersection(clone_movie['director'])
                            temp_score=0
                            for i in common_director:
                                temp_score=temp_score+user_profile['directors'][i]
                            score=score+ 0.0218 * ((temp_score*1.0/no_of_movies)/no_of_feature)

                            common_cast=set(user_profile['cast']).intersection(clone_movie['cast'])
                            temp_score=0
                            for i in common_cast:
                                temp_score=temp_score+user_profile['cast'][i]
                            score=score+ 0.1042 * ((temp_score*1.0/no_of_movies)/no_of_feature)

                            common_writer=set(user_profile['writers']).intersection(clone_movie['writer'])
                            temp_score=0
                            for i in common_writer:
                                temp_score=temp_score+user_profile['writers'][i]
                            score=score+ 0.0190 * ((temp_score*1.0/no_of_movies)/no_of_feature)

                            score += 0.0297 * (clone_movie['rating']/no_of_movies/no_of_feature)

                            similarity_value[movie]=score
                            #print score, movie['title']
                        except KeyError:
                            key_error += 1
                            pass
                    #print type(sorted_list.reverse())
                    del movie_list


                except EOFError:
                    break

        print "GENERATING TOP N RECOMMENDATIONS...", count, key_error
        sorted_list = sorted(similarity_value.items(), key=operator.itemgetter(1),reverse=True)
        print n
        print len(sorted_list)
        print len(similarity_value.keys())
        count = 0
        for i in range(0,len(sorted_list)):
            print sorted_list[i][0].movieID, sorted_list[i][1]
            if count < n and sorted_list[i][0] not in user_movie_list:
                recommendation_list.append(sorted_list[i][0])
                count +=1
            elif count >= n:
                break
        print type(recommendation_list[0])
        return recommendation_list