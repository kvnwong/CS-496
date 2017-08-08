package cs496.androidhttpandoauth;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    /** Called when the user taps the HTTP and OAuth button */
    public void enterIn(View view) {
        Intent intent = new Intent(this, APIActivity.class);
        startActivity(intent);
    }
}
