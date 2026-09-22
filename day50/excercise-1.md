# Exercise: MovieLens Popular Movies using AWS Lambda

## Objective

Create a Python AWS Lambda function that identifies popular movies from the MovieLens dataset.

## Input

The following files are stored in Amazon S3:

- `movies.csv`
- `ratings.csv`

## Task

Create a Python Lambda function that:

1. Reads `movies.csv` and `ratings.csv` from S3.
2. Calculates the following for each movie:
   - Average rating (`avg_rating`)
   - Total number of ratings (`total_ratings`)
3. Selects movies that satisfy:

```
avg_rating >= 4.0
   total_ratings >= 100
```


4. Joins the result with `movies.csv` to get the movie title.
5. Sorts the results by average rating in descending order.
6. Stores the result back into S3.

## Expected Output

The output should contain:

- `movieId`
- `title`
- `avg_rating`
- `total_ratings`

Example:

| movieId | title | avg_rating | total_ratings |
|---------|-------|------------|---------------|
| 318 | Shawshank Redemption | 4.42 | 317 |
| 858 | Godfather | 4.29 | 192 |

## Requirements

- Use Python.
- Use AWS Lambda.
- Use `boto3` to access S3.
- Input and output should be stored in S3.
- Log the number of movies processed and the number of popular movies found.
