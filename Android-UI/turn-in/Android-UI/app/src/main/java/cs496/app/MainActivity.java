package cs496.app;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button btn_hor = (Button) findViewById(R.id.horizontal);
        btn_hor.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, display_horizontal.class);
                startActivity(intent);
            }
        });

        Button btn_vert = (Button) findViewById(R.id.verticle);
        btn_vert.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, display_verticle.class);
                startActivity(intent);
            }
        });

        Button btn_grid = (Button) findViewById(R.id.grid);
        btn_grid.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, display_grid.class);
                startActivity(intent);
            }
        });

        Button btn_rel = (Button) findViewById(R.id.relative);
        btn_rel.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, display_relative.class);
                startActivity(intent);
            }
        });
    }
}
