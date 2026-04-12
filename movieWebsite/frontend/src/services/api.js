const API_KEY='c4ea3fbecfb67b559e81d9c4c5a5f717';
const BASE_URL='https://api.themoviedb.org/3';

export const getPopularMovies = async () =>{ // async just means it will take some time to make the request so wait till then
    const response = await fetch(`${BASE_URL}/movie/popular?api_key=${API_KEY}`);
    const data= await response.json();
    return data.results;
};

export const searchMovies = async (query) =>{ // async just means it will take some time to make the request so wait till then
    const response = await fetch(`${BASE_URL}/search/novie?api_key=${API_KEY}&query=${encodeURIComponent(query)}`);
    const data= await response.json();
    return data.results;
};
