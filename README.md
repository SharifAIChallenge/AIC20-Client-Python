# Requirements 

## Build

After implementing your code in `AI.py`, you may need to run it. 
Below are the instructions to build and execute the client project.

![AI](http://s7.picofile.com/file/8388348218/AI.JPG)

### Using Command Line

To fetch and build the project use the following commands:

```
cd <path to working directory>
git clone https://github.com/SharifAIChallenge/AIC20-Client-Python
cd AIC20-Client-Python
```

Now you have to run the server ".jar" file and then you should `controller.py` 4 times. Each time you run controller a new client connects to the game. You can implement different AIs for different clients and run their controllers seperately.

### Using Pycharm

You can download Jetbrains Pycharm from this [link](https://www.jetbrains.com/pycharm/download/).

This IDE allows quick and easier usage.

1) Run the server using the command line located below the page in Pycharm and enter the following code:
```
cd your_server_directory/
java -jar server_jar_file.jar
```

2) Run `controller.py` by right clicking and choosing `Run 'controller'` option:

![run_controller](http://s6.picofile.com/file/8388348318/Run_controller.JPG)

3) Allow parallel runs: 
* Click on the configuration of python
* Choose `edit Configurations`
![edit_config](http://s7.picofile.com/file/8388348276/edit_configuration.JPG)
* Click the check box with label `Allow parallel run`
![allow_parallel](http://s7.picofile.com/file/8388348250/allow_parallel.JPG)
* run the controller again for four times

## Multiple codes

For multiple codes you can copy the rest of the client source code and simply change the `AI.py` file as you will. Then run the controller for each source code

