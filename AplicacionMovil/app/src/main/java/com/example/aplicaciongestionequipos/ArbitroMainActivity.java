package com.example.aplicaciongestionequipos;

import android.content.Intent;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.card.MaterialCardView;

public class ArbitroMainActivity extends AppCompatActivity {

    MaterialCardView cardVerPartidos, cardCrearPartido, cardGestionarTarjetas, cardVerJugadores, cardAgregarJugador;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_arbitro_main);

        cardVerPartidos = findViewById(R.id.cardVerPartidos);
        cardCrearPartido = findViewById(R.id.cardCrearPartido);
        cardGestionarTarjetas = findViewById(R.id.cardGestionarTarjetas);
        cardVerJugadores = findViewById(R.id.cardVerJugadores);
        cardAgregarJugador = findViewById(R.id.cardAgregarJugador);

        cardVerPartidos.setOnClickListener(view -> {
            Intent intent = new Intent(this, VerPartidosActivity.class);
            startActivity(intent);
        });

        cardCrearPartido.setOnClickListener(view -> {
            Intent intent = new Intent(this, CrearPartidoActivity.class);
            startActivity(intent);
        });

        cardGestionarTarjetas.setOnClickListener(view -> {
            Intent intent = new Intent(this, GestionarTarjetasActivity.class);
            startActivity(intent);
        });

        cardVerJugadores.setOnClickListener(view -> {
            Intent intent = new Intent(this, VerJugadoresActivity.class);
            startActivity(intent);
        });

        cardAgregarJugador.setOnClickListener(view -> {
            Intent intent = new Intent(this, AgregarJugadorActivity.class);
            startActivity(intent);
        });
    }
}
