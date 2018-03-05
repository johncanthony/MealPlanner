# MealPlanner API V1


## Endpoints

### GET /api/v1/dishes/
Description: Pulls a list of first 10 dishes

Parameters: 
    
* (Optional) cursor : <integer> 
 * Moves the cursor to pull a set of dishes starting from the cursor point
 * Example : /api/v1/dishes/?cursor=5

* (Optional) count : <integer>
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

### GET /api/v1/dishes/dish
Description: Pulls the ingredients for a single dish

Parameters:

    * dish : naked string with %20 in spaces
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
    400 - No dish provided


