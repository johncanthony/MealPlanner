# MealPlanner API V1


## Endpoints
[http://www.example.com/api/v1/dishes/](#/api/v1/dishes/)

[http://www.example.com/api/v1/dishes/dish/](#/api/v1/dishes/dish)

[http://www.example.com/api/v1/dishes/search](#/api/v1/dishes/search)

### /api/v1/dishes/
Description: Pulls a list of first 10 dishes

#### Method: GET

Parameters: 
    
* (Optional) cursor 
  * Type: integer
  * Moves the cursor to pull a set of dishes starting from the cursor point
  * Example : /api/v1/dishes/?cursor=5

* (Optional) count 
  * Type: integer
  * Changes the total number of dishes pulled by the query. Note: depending on current cursor location, the returned list may be shorter than the count provided
  * Example : /api/v1/dishes/?count=25

Returns:

    JSON

    ```
    {
     status: string success
     cursor: integer cursor position
     dishes: [] array of dish names
    }
    ```

### /api/v1/dishes/dish

#### Method: GET

Description: Pulls the ingredients for a single dish

Parameters:

* dish 
  * Type: naked string with %20 in spaces
  * Specifies the dish being queried
  * Example: /api/v1/dishes/dish/?dish=Hot%20Dogs

Returns:

    JSON 
    
    ```
    {
     status: string - success/fail
     //status: success
     data: [] - array of ingredients
     key : string - name of the dish

    //status: fail
    error: string - error message     
    }
    ```

Error:
    Response Code: 400  
   * Dish parameter not provided

#### Method: Post

#### TODO

### /api/v1/dishes/search

#### Method : GET

Description: Query all dishes given a partial string or keyword

Parameters:

* query 
  * Type: naked string with %20 in spaces
  * Partial string or keyword for dishes
  * Example: /api/v1/dishes/search/?query=Hot%20Dogs

Returns:

    JSON 
    
    ```
    {
     status: string - success/fail
     //status: success
     data: [] - array of ingredients

    //status: fail
    error: string - error message     
    }
    ```
