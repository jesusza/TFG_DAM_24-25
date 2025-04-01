package com.example.aplicaciongestionequipos;

public class Partido {
    public String equipo_local;
    public String equipo_visitante;
    public String fecha;
    public String hora;
    public String estado;
    public int goles_local;
    public int goles_visitante;

    public Partido() {} // Requerido por Firestore

    public Partido(String equipo_local, String equipo_visitante, String fecha, String hora, String estado) {
        this.equipo_local = equipo_local;
        this.equipo_visitante = equipo_visitante;
        this.fecha = fecha;
        this.hora = hora;
        this.estado = estado;
    }
}
